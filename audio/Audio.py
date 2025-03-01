import wave
import struct


class AudioTreatment:
    
    @staticmethod    
    def amplifier(input, output, factor):
        with wave.open(input, 'rb') as wav:
            params = wav.getparams()
            channels, sampwidth, framerate, frames, comptype, compname = params
            if channels != 1:
                print("Erreur : ce programme gère uniquement le mono.")
                return
            with wave.open(output, 'wb') as out:
                out.setparams(params)
                for _ in range(frames):
                    frame = wav.readframes(1)
                    sample = struct.unpack('<h', frame)[0]
                    new_sample = int(sample * factor)
                    if new_sample > 32767:
                        new_sample = 32767
                    elif new_sample < -32768:
                        new_sample = -32768
                    out.writeframes(struct.pack('<h', new_sample))

    @staticmethod
    def antidistortion(input, output):
        with wave.open(input, 'rb') as wav:
            params = wav.getparams()
            channels, sampwidth, framerate, frames, comptype, compname = params
            if channels != 1:
                print("Erreur : ce programme gère uniquement le mono.")
                return
            samples = []
            for _ in range(frames):
                frame = wav.readframes(1)
                sample = struct.unpack('<h', frame)[0]
                samples.append(sample)
            maxAmpl = max(abs(s) for s in samples)
            if maxAmpl == 0:
                factor = 1
            else:
                factor = 32767 / maxAmpl
            with wave.open(output, 'wb') as out:
                out.setparams(params)
                for s in samples:
                    new_sample = int(s * factor)
                    out.writeframes(struct.pack('<h', new_sample))

    @staticmethod
    def antibruit(input, output, threshold):
        with wave.open(input, 'rb') as wav:
            params = wav.getparams()
            channels, sampwidth, framerate, frames, comptype, compname = params
            if channels != 1:
                print("Erreur : ce programme gère uniquement le mono.")
                return
            with wave.open(output, 'wb') as out:
                out.setparams(params)
                for _ in range(frames):
                    frame = wav.readframes(1)
                    sample = struct.unpack('<h', frame)[0]
                    if abs(sample) < threshold:
                        new_sample = 0
                    else:
                        new_sample = sample
                    out.writeframes(struct.pack('<h', new_sample))
