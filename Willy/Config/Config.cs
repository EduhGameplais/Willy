using Mighty;
using Newtonsoft.Json;

public static class Config
{
    public static dynamic LoadConfig(string filePath)
    {
        Log.PrintLn("$Yellow$Lendo configurações...");
        if (!File.Exists(filePath))
        {
            throw new FileNotFoundException("Arquivo de configuração não encontrado.", filePath);
        }

        string json = File.ReadAllText(filePath);
        var data = JsonConvert.DeserializeObject(json);
        Log.PrintLn("$Green$Configurações carregadas...");
        return data;
    }
}