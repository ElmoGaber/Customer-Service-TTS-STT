# Theoretical Notes — STT & TTS fundamentals

## 1. What is STT (ASR)
Automatic Speech Recognition (ASR) maps an audio waveform x(t) to a sequence of tokens/words y = (y1, y2, ..., yN). Modern systems use deep neural networks (RNNs, CNNs, Transformers) with connectionist temporal classification (CTC), attention/seq2seq, or hybrid architectures.

## 2. Model families (brief)
- **CTC-based** (e.g., Wav2Vec2 pretrained + CTC head): good for alignment-free training.
- **Seq2seq with attention** (e.g., encoder-decoder + attention): better for end-to-end punctuation/casing.
- **Transducer (RNN-T / Transformer Transducer)**: optimized for streaming low-latency systems.
- **Whisper-like**: encoder-decoder transformer trained on massive corpora; strong multilingual performance.

## 3. Training vs Inference modes
- **Training:** heavy compute, uses teacher forcing, optimizes a loss (CTC loss, cross-entropy, transducer loss).
- **Inference:** may be beam search (higher accuracy, slower) or greedy/CTC decode (faster, lower accuracy). Streaming inference uses chunked/online methods (low-latency decoding, incremental outputs).

## 4. Loss functions (high level)
- **CTC Loss:** aligns input frames with output labels by marginalizing over possible alignments.
- **Cross-entropy (seq2seq):** standard token-level loss in auto-regressive models.
- **Transducer Loss:** combines alignment and prediction in streaming-capable model.

## 5. Evaluation metrics
- **Word Error Rate (WER):**
  \nWER = (S + D + I) / N\n
  where S=substitutions, D=deletions, I=insertions, N=number of words in reference.
  - Use normalized text (case folding, punctuation removal) for fair comparison.
  - Tools: `jiwer` (we use default transforms + RemovePunctuation per methodology).

- **Words Per Minute (WPM) / Throughput:**
  \nWPM = (number_of_words_in_transcript) / (latency_seconds / 60)\n

- **Latency:** measured in ms from request to first-final transcript and end-to-end round-trip.

- **Confidence & Calibration:** model-provided confidence can be used as proxy for fallback decisions but is not comparable across providers.

## 6. Diarization & Speaker-attribution
- Diarization segments audio by speaker (may use external models like pyannote.audio).
- Important for multi-party meetings and for accurate WER per-speaker.

## 7. Preprocessing steps
- Resample to model's sample rate (e.g., 16kHz or 16k).
- Normalize loudness (LUFS) and apply VAD to remove silence.
- Noise reduction (spectral subtraction, Wiener filter) for noisy channels.

## 8. TTS fundamentals (overview)
- **Acoustic model** (e.g., Tacotron): maps text → mel-spectrogram.
- **Vocoder** (e.g., WaveGlow, HiFi-GAN, VITS): mel → waveform.
- **Neural TTS**: generative models producing natural prosody and intonation. VITS supports end-to-end variational flow, lower latency.

## 9. Trade-offs & design choices
- **Accuracy vs Latency:** beam search increases accuracy but adds ms; choose beam width for server-side offline vs real-time.
- **Cloud vs Local:** cloud often offers better accuracy and language coverage; local yields control, privacy, and potential cost benefits.
- **Model size vs throughput:** large models give better accuracy but require GPU & memory.

## 10. Datasets & benchmarking samples
- Short-form test: ~30s clips from VoxPopuli / Common Voice.
- Medium-form: 4–5 minute interviews.
- Long-form: 30–40 minute panels (preprocessed for upload limits).
- For non-English: include validated transcripts from multilingual corpora.

## 11. Ethical considerations
- Consent for audio recording, PII handling in transcripts, bias in training data for accents/dialects.

## 12. Recommended reading / references
- Papers: Wav2Vec2, RNN-T, Whisper paper
- Tools: jiwer (WER), pyannote (diarization)

