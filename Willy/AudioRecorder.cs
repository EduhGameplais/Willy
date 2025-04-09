using Mighty;
using OpenTK.Audio.OpenAL;

namespace Willy;

    public class AudioRecorder
    {
        private const int SampleRate = 16000;
        private const int BufferSize = 512;
        private float _silenceThreshold = 0.05f; // Adjust as needed
        private int _silenceDurationMs = 2000; // 2 seconds of silence to stop

        private readonly string _outputFileName;
        private ALCaptureDevice _captureDevice;
        private bool _isRecording;
        private CancellationTokenSource _cancellationTokenSource;

        public AudioRecorder(string outputFileName = "recording.wav", float silenceThreshold = 0.05f, int silenceDurationMs = 2000)
        {
            _outputFileName = outputFileName;
            _silenceThreshold = silenceThreshold;
            _silenceDurationMs = silenceDurationMs;
        }

        public async Task StartRecordingAsync()
        {
            // Initialize capture device
            _captureDevice = ALC.CaptureOpenDevice(null, SampleRate, ALFormat.Mono16, BufferSize);
            
            if (_captureDevice == IntPtr.Zero)
            {
                throw new Exception("Could not open audio capture device.");
            }

            _isRecording = true;
            _cancellationTokenSource = new CancellationTokenSource();
            
            // Start capture
            ALC.CaptureStart(_captureDevice);
            
            Log.PrintLn("$Yellow$Gravação iniciada.");
            
            // Record in a separate thread
            await Task.Run(() => RecordAudioWithSilenceDetection(_cancellationTokenSource.Token));
        }

        public void StopRecording()
        {
            _isRecording = false;
            _cancellationTokenSource?.Cancel();
        }

        private void RecordAudioWithSilenceDetection(CancellationToken cancellationToken)
        {
            using (var memoryStream = new MemoryStream())
            {
                using (var writer = new BinaryWriter(memoryStream))
                {
                    // WAV header
                    WriteWavHeader(writer, 0); // Temporary size
                    
                    short[] buffer = new short[BufferSize];
                    int silenceCounter = 0;
                    long dataSize = 0;
                    DateTime lastActivity = DateTime.Now;
                    DateTime startedRecording = DateTime.Now;
                    
                    while (_isRecording && !cancellationToken.IsCancellationRequested)
                    {
                        // Correctly retrieve available samples
                        int samplesAvailable = ALC.GetInteger(_captureDevice, AlcGetInteger.CaptureSamples);
                        
                        if (samplesAvailable >= BufferSize)
                        {
                            ALC.CaptureSamples(_captureDevice, buffer, BufferSize);
                            
                            // Check if there's sound (non-silence)
                            bool hasSpeech = HasSpeech(buffer, _silenceThreshold);
                            
                            if (hasSpeech)
                            {
                                lastActivity = DateTime.Now;
                                silenceCounter = 0;
                            }
                            else
                            {
                                // Count silence duration
                                if ((DateTime.Now - lastActivity).TotalMilliseconds > _silenceDurationMs)
                                {
                                    // Enough silence detected to stop recording
                                    var elapsedTime = DateTime.Now - startedRecording;
                                    Log.PrintLn($"$Blue$Limite de Silencio atingido. Parando Gravação. ({elapsedTime.Minutes}m, {elapsedTime.Seconds}s)");
                                    break;
                                }
                            }
                            
                            // Write audio data
                            foreach (short sample in buffer)
                            {
                                writer.Write(sample);
                                dataSize += 2; // 2 bytes per sample
                            }
                        }
                        
                        Thread.Sleep(10); // Small pause to avoid excessive CPU usage
                    }
                    
                    // Close capture
                    ALC.CaptureStop(_captureDevice);
                    ALC.CaptureCloseDevice(_captureDevice);
                    
                    // Go back to the start of the stream and update WAV header
                    memoryStream.Position = 0;
                    WriteWavHeader(writer, dataSize);
                    
                    // Save the file
                    using (var fileStream = new FileStream(_outputFileName, FileMode.Create))
                    {
                        memoryStream.Position = 0;
                        memoryStream.CopyTo(fileStream);
                    }
                    
                    Log.PrintLn($"$Green$Gravação salva em: {_outputFileName}");
                }
            }
        }

        private bool HasSpeech(short[] buffer, float threshold)
        {
            // Calculate RMS (Root Mean Square) of the buffer
            double sum = 0;
            for (int i = 0; i < buffer.Length; i++)
            {
                sum += buffer[i] * buffer[i];
            }
            
            double rms = Math.Sqrt(sum / buffer.Length);
            double normalizedRms = rms / short.MaxValue;
            
            return normalizedRms > threshold;
        }

        private void WriteWavHeader(BinaryWriter writer, long dataSize)
        {
            // RIFF header
            writer.Write(new char[] { 'R', 'I', 'F', 'F' });
            writer.Write((int)(dataSize + 36)); // Total size - 8
            writer.Write(new char[] { 'W', 'A', 'V', 'E' });
            
            // fmt header
            writer.Write(new char[] { 'f', 'm', 't', ' ' });
            writer.Write(16); // fmt block size
            writer.Write((short)1); // PCM
            writer.Write((short)1); // Mono
            writer.Write(SampleRate);
            writer.Write(SampleRate * 2); // Byte rate
            writer.Write((short)2); // Block align
            writer.Write((short)16); // Bits per sample
            
            // Data header
            writer.Write(new char[] { 'd', 'a', 't', 'a' });
            writer.Write((int)dataSize);
        }
    }