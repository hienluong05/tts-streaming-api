import io
import wave
import numpy as np
import soundfile as sf

def numpy_to_wav_bytes(audio_array: np.ndarray, sample_rate: int) -> bytes:
    """Convert numpy array to WAV bytes."""
    with io.BytesIO() as wav_io:
        sf.write(wav_io, audio_array, sample_rate, format='WAV', subtype='PCM_16')
        return wav_io.getvalue()

def create_wav_header(sample_rate: int, num_channels: int = 1, bit_depth: int = 16) -> bytes:
    """Creates a WAV header for streaming PCM data."""
    # Since streaming, we might not know the exact file size upfront.
    # Using 0xFFFFFFFF for chunk sizes is a common trick for streaming WAV.
    with io.BytesIO() as wav_io:
        with wave.open(wav_io, 'wb') as wave_writer:
            wave_writer.setnchannels(num_channels)
            wave_writer.setsampwidth(bit_depth // 8)
            wave_writer.setframerate(sample_rate)
            # Write a dummy frame to create the header
            wave_writer.writeframes(b'')
        
        # Modify the riff and data chunk sizes to "unknown" (0xFFFFFFFF)
        header = bytearray(wav_io.getvalue())
        header[4:8] = b'\xff\xff\xff\xff'
        header[40:44] = b'\xff\xff\xff\xff'
        return bytes(header)

def numpy_to_pcm16_bytes(audio_array: np.ndarray) -> bytes:
    """Convert float32 numpy array to 16-bit PCM bytes."""
    # Ensure range [-1.0, 1.0]
    audio_array = np.clip(audio_array, -1.0, 1.0)
    # Convert to 16-bit PCM
    pcm16 = (audio_array * 32767.0).astype(np.int16)
    return pcm16.tobytes()
