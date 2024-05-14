import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._
import org.apache.spark.ml.feature.{StopWordsRemover, CountVectorizer}
import org.apache.spark.ml.Pipeline
import org.apache.spark.ml.feature.RegexTokenizer

object DataPreprocessing {
  def main(args: Array[String]): Unit = {
    // Configuration Spark
    val spark = SparkSession.builder()
      .appName("DataPreprocessing")
      .config("spark.master", "local[4]")  // Utilisation de 4 threads locaux
      .getOrCreate()

    // Charger les données à partir du fichier texte
    val data = spark.read.text("output/book_1.txt")

    // Prétraitement des données
    val cleanData = preprocessData(data, spark)

    // Afficher les premières lignes des données prétraitées
    println("Clean Data:")
    cleanData.show(truncate = false)

    // Arrêter la session Spark
    spark.stop()
  }

  def preprocessData(data: DataFrame, spark: SparkSession): DataFrame = {
    // Convertir les lignes en tokens et les normaliser
    val tokenizer = new RegexTokenizer()
      .setInputCol("value")
      .setOutputCol("words")
      .setPattern("\\W+")  // Séparer les mots par des caractères non alphanumériques
      .setToLowercase(true)

    // Supprimer les mots vides (stop words)
    val remover = new StopWordsRemover()
      .setInputCol("words")
      .setOutputCol("filteredWords")

    // Vectoriser les mots
    val vectorizer = new CountVectorizer()
      .setInputCol("filteredWords")
      .setOutputCol("features")

    // Créer un pipeline de traitement
    val pipeline = new Pipeline()
      .setStages(Array(tokenizer, remover, vectorizer))

    // Appliquer le pipeline sur les données
    val cleanData = pipeline.fit(data).transform(data)

    cleanData
  }
  //Rajouter du code ici qui permet de récupérer le fichier traité au format txt
  //Le fichier traité sera alors utile pour l'analyse de sentiment et le reste du projet
}
