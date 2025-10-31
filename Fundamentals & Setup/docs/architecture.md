# Architecture — voice-ai-benchmark (Week 1)

## Goal
شرح معماري واضح للنظام الذي سنختبره: يوضح مكونات STT/TTS، مسارات البيانات، نقاط القياس للـ latency، وأشكال النشر (local vs cloud, streaming vs batch).

## High-level components
1. **Audio Input Layer**
   - Sources: mic (streaming), uploaded files (batch), telephony streams.
   - Preprocessing: resampling, normalization, voice activity detection (VAD), noise gating.

2. **STT Layer**
   - Provider adapters (Google/Azure/Deepgram/AssemblyAI/Whisper-local).
   - Responsibilities: receive audio chunk or file → preprocess → send to model/API → return transcript + metadata (confidence, segments, timestamps).
   - Modes: streaming (chunked real-time) و batch (file-at-once).

3. **Post-processing Layer**
   - Text normalization (numbers, punctuation options), punctuation restoration (if model doesn't provide), casing.
   - Diarization & speaker-attribution (optional external module).
   - Fallback & confidence-based routing (e.g., if confidence < threshold → use alternative model or ask for re-transmission).

4. **TTS Layer** (for end-to-end demo)
   - Text → TTS module (VITS/Coqui/Tacotron variants).
   - Audio post-processing (leveling, loudness normalization).
   - Integration with Avatar / lip-sync API (module export).

5. **Evaluation & Monitoring**
   - Metrics store: WER, Latency (per request & end-to-end), WPM, Model size, Memory & GPU utilization.
   - Logs: per-provider detailed logs + central benchmark log.
   - Dashboards: (future) simple local web UI (Gradio) for test replay + metric charts.

## Data flows (streaming vs batch)
- **Batch**: file uploaded → single STT request → full transcript → post-process → metrics.
- **Streaming**: audio chunks → local VAD → chunk send to STT streaming endpoint → streaming transcript partials → assemble → finalize → post-process.
- **Latency path**: microphone capture → preprocessing → network (if cloud) → model inference → return → postprocessing → playback (TTS) → avatar sync.

## Latency measurement points (where to time)
- Capture → Preprocess start
- Preprocess end → Send to provider
- Provider receive → Provider send back (inference)
- Postprocess end → Final transcript available
- (End-to-end) Microphone in → Audio out (TTS) ready

## Failover & resilience
- Timeouts per-provider (e.g., 5s for short chunks); if timeout, route to fallback provider.
- Graceful degradation: partial transcript + confidence flag returned to user.

## Deployment notes
- Local (development): Whisper local on GPU, others as placeholders or API-mode (with keys).
- Cloud (production): choose provider(s) by cost/latency tradeoff; route streaming to low-latency provider.
- Scaling: horizontally scale STT adapters in containerized workers; use a message queue for high throughput streaming ingestion.

## Security & Privacy
- Avoid storing raw audio longer than necessary; encrypt logs if containing PII.
- Mask or redact sensitive fields (credit card, IDs) in transcripts when storing.

