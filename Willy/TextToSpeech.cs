using System.Diagnostics;
using EdgeTTS;
using PiperSharp;
using Mighty;
using PiperSharp.Models;

namespace Willy;

public class TextToSpeech
{
    private readonly string _engine;
    private readonly string? _model;
    
    //Piper
    private readonly PiperProvider? _piperModel;
    
    public TextToSpeech(dynamic ttsConfig)
    {
        _engine = (string)ttsConfig.Engine;
        
        switch (_engine.ToLower())
        {
            case "piper" or "pipertts":
                Log.PrintLn("$Yellow$Carregando PiperTTS...");
                
                _model = (string)ttsConfig.PiperTTS.Model;
                
                var model = PiperDownloader.TryGetModelByKey(_model).GetAwaiter().GetResult();
                var modelPiper = PiperDownloader.DownloadModelByKey(_model).GetAwaiter().GetResult(); //model ?? 
                
                var cwd = Directory.GetCurrentDirectory();
                _piperModel = new PiperProvider(new PiperConfiguration()
                {
                    ExecutableLocation = Path.Join(cwd, "Piper", "piper"), // Path to piper executable
                    WorkingDirectory = Path.Join(cwd, "Piper"), // Path to piper working directory
                    Model = modelPiper!, // Loaded/downloaded VoiceModel
                });
                Log.PrintLn("$Green$PiperTTS Carregado.");
                break;
            case "edge" or "edgetts":
                Log.PrintLn("$Green$Usando EdgeTTS...");
                _model = (string)ttsConfig.EdgeTTS.Voice;
                break;
            default:
                throw new Exception($"Unknown TTS engine: {_engine}");
        }
    }
    
    public async Task SpeakAsync(string text)
    {
        switch (_engine.ToLower())
        {
            case "piper" or "pipertts":
                try
                {
                    Log.PrintLn($"$Yellow$Usando $Blue${_engine} $Yellow$para falar $Blue$\"{text}\"$Yellow$...");
                    var result = _piperModel!.InferAsync(text, AudioOutputType.Wav).GetAwaiter().GetResult();

                    await PlayWavAsync(result);
                    Log.PrintLn("$Green$Reprodução de audio finalizada.");
                }
                catch (Exception e)
                {
                    Log.PrintError(e, "Erro ao processar ou reproduzir o áudio sintetizado.(PiperTTS)");
                }
                break;
            case "edge" or "edgetts":
                try
                {
                    Log.PrintLn($"$Yellow$Usando $Blue${_engine} $Yellow$para falar $Blue$\"{text}\"$Yellow$...");
                    var tempPath = Path.GetTempFileName() + ".wav";
                
                    var communicate = new Communicate(
                        text, _model!);
                    communicate.Save(tempPath).GetAwaiter().GetResult();
                
                    PlayWavAsyncFile(tempPath).GetAwaiter().GetResult();
                
                    File.Delete(tempPath);
                    Log.PrintLn("$Green$Reprodução de audio finalizada.");
                }
                catch (Exception e)
                {
                    Log.PrintError(e, "Erro ao processar ou reproduzir o áudio sintetizado.(EdgeTTS)");
                }
                break;
        }
    }
    
    private static async Task PlayWavAsyncFile(string filePath)
    {
        var startInfo = new ProcessStartInfo
        {
            FileName = "ffplay",
            Arguments = $"-nodisp -autoexit \"{filePath}\"",
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true,
        };

        using var proc = new Process();
        proc.StartInfo = startInfo;
        proc.Start();

        // opcional: lê a saída para garantir que o buffer não bloqueie
        _ = proc.StandardOutput.ReadToEndAsync();
        _ = proc.StandardError.ReadToEndAsync();

        await proc.WaitForExitAsync();
    }
    
    private static async Task PlayWavAsync(byte[] wavData)
    {
        var tempPath = Path.GetTempFileName() + ".wav";
        await File.WriteAllBytesAsync(tempPath, wavData);

        var startInfo = new ProcessStartInfo
        {
            FileName = "ffplay",
            Arguments = $"-nodisp -autoexit \"{tempPath}\"",
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true,
        };

        using var proc = new Process();
        proc.StartInfo = startInfo;
        proc.Start();

        // opcional: lê a saída para garantir que o buffer não bloqueie
        _ = proc.StandardOutput.ReadToEndAsync();
        _ = proc.StandardError.ReadToEndAsync();

        await proc.WaitForExitAsync();
        File.Delete(tempPath);
    }
}