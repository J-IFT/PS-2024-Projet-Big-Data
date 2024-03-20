import org.apache.spark.sql.SparkSession

object DataCollection {
  def main(args: Array[String]): Unit = {
    // Créer une session Spark
    val spark = SparkSession.builder()
      .appName("DataCollection")
      .master("local")
      .getOrCreate()

    // Charger les données à partir d'un fichier texte
    val data = spark.read.text("../data/*.txt")

    // Afficher les premières lignes des données
    data.show()

    // Autres opérations de collecte et de structuration des données

    // Arrêter la session Spark
    spark.stop()
  }
}
