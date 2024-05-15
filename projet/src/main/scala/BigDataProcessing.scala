import org.apache.spark.sql.{Dataset, SparkSession}
import org.apache.spark.sql.Encoders.STRING

object BigDataProcessing {
  def main(args: Array[String]): Unit = {
    // Créer une session Spark
    val spark = SparkSession.builder()
      .appName("BigData")
      .config("spark.master", "local[4]")
      .getOrCreate()

    // Importer les implicits Spark pour l'encodage
    import spark.implicits._
    
    // Charger les données depuis le fichier texte
    val data = spark.read.textFile("output/petitbook4traitéparunehumaine.txt")

    // Prétraiter les données
    val processedData = preprocessData(data, spark)

    // Sauvegarder les données prétraitées au format CSV
    processedData.write.csv("output/bigdata/")

    // Arrêter la session Spark
    spark.stop()
  }

  def preprocessData(data: Dataset[String], spark: SparkSession): Dataset[String] = {
    // Appliquer le prétraitement (tokenisation, conversion en minuscules)
    val processedData = data.flatMap(line => line.toLowerCase.split("\\W+"))(STRING) // Utilisation de l'encodeur pour String
    
    processedData
  }
}
