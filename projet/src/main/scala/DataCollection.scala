import org.apache.spark.sql.SparkSession
import org.apache.spark.SparkConf

object DataCollection {
  def main(args: Array[String]): Unit = {
    // Configuration Spark
    val conf: SparkConf = new SparkConf()
      .setMaster("local[4]")  // Utilisez 4 threads locaux
      .setAppName("DataCollection")
      .set("spark.driver.host", "localhost")  // Définir l'hôte du pilote
      .set("spark.testing.memory", "2147480000")  // Définir la mémoire de test (optionnel)

    // Créer une session Spark avec la configuration définie
    val spark = SparkSession.builder()
      .config(conf)
      .getOrCreate()

    // Charger les données à partir de chaque fichier texte
    val data1 = spark.read.text("../data/books_large_p1.txt")
    val data2 = spark.read.text("../data/books_large_p2.txt")

    // Afficher les premières lignes des données
    println("Data from file1:")
    data1.show()

    println("Data from file2:")
    data2.show()

    // Autres opérations de collecte et de structuration des données

    // Arrêter la session Spark
    spark.stop()
  }
}
