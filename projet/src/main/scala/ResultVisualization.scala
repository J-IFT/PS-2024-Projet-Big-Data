import scala.sys.process._

object ResultVisualization {
  def main(args: Array[String]): Unit = {
    // Chemin vers le script Python que tu veux exécuter
    val pythonScriptPath = "scripts/ResultVisualization.py"

    // Créer un ProcessBuilder pour exécuter le script Python
    val pb = Process(pythonScriptPath)

    // Démarrer le processus
    val process = pb.run()

    // Attendre que le processus se termine
    val exitCode = process.exitValue()

    // Afficher le code de sortie
    println(s"Le script Python s'est terminé avec le code de sortie : $exitCode")
  }
}