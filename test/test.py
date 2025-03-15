from djelia import Djelia


client = Djelia(api_key="API key here")

languages = client.get_supported_languages()
print("testing supported languages endpoint........")
print("Supported languages:", languages)


print("testing translatino endpoint........")
translation = client.translate(
    text="Hello, how are you doing today?", 
    source="en", 
    target="bam"
)
print("Translation:", translation["text"])


print("testing transcription v1 endpoint........")
result_v1 = client.transcribe("test1.wav")
for segment in result_v1:
    print(f"V1 Transcription: {segment['text']} ({segment['start']} - {segment['end']})")

print("testing transcription v2 endpoint........")
result_v2 = client.transcribe("test1.wav", version=2)
for segment in result_v2:
    print(f"V2 Transcription: {segment['text']} ({segment['start']} - {segment['end']})")


print("testing straming with transcription v2 endpoint........")
# Streaming transcription with V2 API
for segment in client.stream_transcribe("test1.wav", version=2):
    print(f"V2 Streaming: {segment['text']} ({segment.get('start', 'N/A')} - {segment.get('end', 'N/A')})")


print("testing TTS endpoint........")
# Text-to-speech with specific speaker voice
audio_path = client.text_to_speech(
    text="Aw ni ce", 
    speaker=1, 
    output_file="greeting.wav"
)
print(f"Audio saved to: {audio_path}")

print("testing speach translation with v2 endpoint........")
# Transcribe with translation to French (works with both V1 and V2)
french_result = client.transcribe("test1.wav", translate_to_french=True, version=2)
print(f"French translation: {french_result['text']}")



