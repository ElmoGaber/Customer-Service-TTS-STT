import pyaudio
import numpy as np
import torch
from torch.nn.functional import pad
import time
from queue import Queue
import sounddevice as sd
from .config import settings

CHUNK = settings.CHUNK
FORMAT = pyaudio.paFloat32
CHANNELS = settings.CHANNELS
RATE = settings.RATE
SILENCE_THRESHOLD = settings.SILENCE_THRESHOLD
SPEECH_CHECK_THRESHOLD = settings.SPEECH_CHECK_THRESHOLD
MAX_SILENCE_DURATION = settings.MAX_SILENCE_DURATION

from pyannote.audio import Pipeline
from pyannote.audio.core.model import Model
from src.utils.config import settings

from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection
import os
import os
import torch
from torch.nn.functional import pad
from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection
from src.utils.config import settings
import numpy as np

from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection


def init_vad_pipeline():
    print("\nInitializing Voice Activity Detection...")

    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    if not hf_token:
        hf_token = "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"
        print("⚠️ Using manual token...")

    print("Using token:", hf_token[:12] + "...")

    # تحميل الموديل الأساسي
    segmentation_model = Model.from_pretrained(
        "pyannote/segmentation",
        use_auth_token=hf_token
    )

    # إنشاء الـ pipeline
    vad_pipeline = VoiceActivityDetection(segmentation=segmentation_model)

    # هنا التعديل المهم — لازم تمرر dict القيم اللي محتاجها داخل instantiate()
    # بالضبط كده:
    vad_pipeline.instantiate({
        "onset": 0.5,             # حساسية بداية الصوت
        "offset": 0.5,            # حساسية نهاية الصوت
        "min_duration_on": 0.2,   # أقل مدة للكلام
        "min_duration_off": 0.2,  # أقل مدة للصمت
    })

    print("✅ Voice Activity Detection pipeline ready.")
    return vad_pipeline


import torch

def detect_speech_segments(vad_pipeline, audio_input, sample_rate=16000):
    """
    كشف الكلام في ملف صوتي أو numpy array
    """
    print(f"\nProcessing audio: {type(audio_input)}")
    speech_segments = []

    if isinstance(audio_input, np.ndarray):
        # تحويل numpy array إلى 2D torch tensor (channels, samples)
        audio_tensor = torch.tensor(audio_input, dtype=torch.float32).unsqueeze(0)
        vad_output = vad_pipeline({"waveform": audio_tensor, "sample_rate": sample_rate})
    else:
        vad_output = vad_pipeline(audio_input)

    for segment, _, _ in vad_output.itertracks(yield_label=True):
        speech_segments.append((segment.start, segment.end))

    print(f"Detected {len(speech_segments)} speech segments.")
    return speech_segments



def record_audio(duration=None):
    """Records audio for a specified duration.
    (باقي الكود سليم زي ما هو)
    """
    if duration is None:
        duration = settings.RECORD_DURATION

    p = pyaudio.PyAudio()

    stream = p.open(
        format=settings.FORMAT,
        channels=settings.CHANNELS,
        rate=settings.RATE,
        input=True,
        frames_per_buffer=settings.CHUNK,
    )

    print("\nRecording...")
    frames = []

    for i in range(0, int(settings.RATE / settings.CHUNK * duration)):
        data = stream.read(settings.CHUNK)
        frames.append(np.frombuffer(data, dtype=np.float32))

    print("Done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_data = np.concatenate(frames, axis=0)
    return audio_data


def record_continuous_audio():
    """Continuously monitors audio and detects speech segments.
    (باقي الكود سليم زي ما هو)
    """
    p = pyaudio.PyAudio()

    stream = p.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )

    print("\nListening... (Press Ctrl+C to stop)")
    frames = []
    buffer_frames = []
    buffer_size = int(RATE * 0.5 / CHUNK)
    silence_frames = 0
    max_silence_frames = int(RATE / CHUNK * 1)
    recording = False

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_chunk = np.frombuffer(data, dtype=np.float32)

            buffer_frames.append(audio_chunk)
            if len(buffer_frames) > buffer_size:
                buffer_frames.pop(0)

            audio_level = np.abs(np.concatenate(buffer_frames)).mean()

            if audio_level > SILENCE_THRESHOLD:
                if not recording:
                    print("\nPotential speech detected...")
                    recording = True
                    frames.extend(buffer_frames)
                frames.append(audio_chunk)
                silence_frames = 0
            elif recording:
                frames.append(audio_chunk)
                silence_frames += 1

                if silence_frames >= max_silence_frames:
                    print("Processing speech segment...")
                    break

            time.sleep(0.001)

    except KeyboardInterrupt:
        pass
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    if frames:
        return np.concatenate(frames)
    return None


def check_for_speech(timeout=0.1):
    """Checks if speech is detected in a non-blocking way.
    (باقي الكود سليم زي ما هو)
    """
    p = pyaudio.PyAudio()

    frames = []
    is_speech = False

    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        for _ in range(int(RATE * timeout / CHUNK)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_chunk = np.frombuffer(data, dtype=np.float32)
            frames.append(audio_chunk)

            audio_level = np.abs(audio_chunk).mean()
            if audio_level > SPEECH_CHECK_THRESHOLD:
                is_speech = True
                break

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    if is_speech and frames:
        return True, np.concatenate(frames)
    return False, None


def play_audio_with_interrupt(audio_data, sample_rate=24000):
    """Plays audio while monitoring for speech interruption.
    (باقي الكود سليم زي ما هو)
    """
    interrupt_queue = Queue()

    def input_callback(indata, frames, time, status):
        """Callback for monitoring input audio."""
        if status:
            print(f"Input status: {status}")
            return

        audio_level = np.abs(indata[:, 0]).mean()
        if audio_level > settings.INTERRUPTION_THRESHOLD:
            interrupt_queue.put(True)

    def output_callback(outdata, frames, time, status):
        """Callback for output audio."""
        if status:
            print(f"Output status: {status}")
            return

        if not interrupt_queue.empty():
            raise sd.CallbackStop()

        remaining = len(audio_data) - output_callback.position
        if remaining == 0:
            raise sd.CallbackStop()
        valid_frames = min(remaining, frames)
        outdata[:valid_frames, 0] = audio_data[
                                    output_callback.position: output_callback.position + valid_frames
                                    ]
        if valid_frames < frames:
            outdata[valid_frames:] = 0
        output_callback.position += valid_frames

    output_callback.position = 0

    try:
        with sd.InputStream(
                channels=1, callback=input_callback, samplerate=settings.RATE
        ):
            with sd.OutputStream(
                    channels=1, callback=output_callback, samplerate=sample_rate
            ):
                while output_callback.position < len(audio_data):
                    sd.sleep(100)
                    if not interrupt_queue.empty():
                        return True, None
        return False, None
    except sd.CallbackStop:
        return True, None
    except Exception as e:
        print(f"Error during playback: {str(e)}")
        return False, None


def transcribe_audio(processor, model, audio_data, sampling_rate=None):
    """Transcribes audio using Whisper.
    (باقي الكود سليم زي ما هو)
    """
    if sampling_rate is None:
        sampling_rate = settings.RATE

    if audio_data is None:
        return ""

    if isinstance(audio_data, torch.Tensor):
        audio_data = audio_data.numpy()

    input_features = processor(
        audio_data, sampling_rate=sampling_rate, return_tensors="pt"
    ).input_features
    predicted_ids = model.generate(input_features)
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    return transcription[0]