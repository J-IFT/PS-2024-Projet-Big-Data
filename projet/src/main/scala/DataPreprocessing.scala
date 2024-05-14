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

    // Sauvegarder les données prétraitées dans un fichier texte
    saveCleanData(cleanData)

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

  def saveCleanData(cleanData: DataFrame): Unit = {
    // Collecter les données prétraitées au format texte dans un seul DataFrame
    val textData = cleanData.select("filteredWords").collect.map(_.getString(0)).mkString("\n")

    // Créer un DataFrame avec une seule colonne et une seule ligne contenant les données prétraitées
    val textDataFrame = cleanData.sparkSession.createDataFrame(Seq(textData)).toDF("text")

    // Sauvegarder les données prétraitées dans un fichier texte
    textDataFrame.write.text("output/clean_data.txt")
  }
}
