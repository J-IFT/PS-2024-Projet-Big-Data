//ETAPE 2 ET 4
import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._
import org.apache.spark.ml.feature.{StopWordsRemover, CountVectorizer}
import org.apache.spark.ml.Pipeline
import org.apache.spark.ml.feature.RegexTokenizer
import java.nio.file.{Files, Paths, StandardOpenOption}
import scala.collection.JavaConverters._

object DataPreprocessing {
	def main(args: Array[String]): Unit = {
		// Configuration Spark
		val spark = SparkSession.builder()
			.appName("DataPreprocessing")
			.config("spark.master", "local[4]")  // Utilisation de 4 threads locaux
			.getOrCreate()

		// Numéro de book a traiter
		val book = 0
		// Charger les données à partir du fichier texte
		val data = spark.read.text("output/book_"+book+".txt")

		// Pour mieux filtrer certains mots
		val blacklist = Seq("isbn")
		val whitelist = Set("no", "go")

		// Prétraitement des données
		val cleanData = preprocessData(data, spark, blacklist, whitelist)

		// Afficher les premières lignes des données prétraitées
		println("Clean Data:")
		cleanData.show(truncate = false)

		// Sauvegarder les données prétraitées dans un fichier texte
		saveData(cleanData, "output/bigdataprocessing/book_"+book+"_clean")

		// Arrêter la session Spark
		spark.stop()
	}

	// Nettoie le dataframe des éléments non-pertinents
	def preprocessData(data: DataFrame, spark: SparkSession, blacklistedWords: Seq[String], whitelistedWords: Set[String]): DataFrame = {
		// Convertir les lignes en tokens et les normaliser
		val tokenizer = new RegexTokenizer()
			.setInputCol("value")
			.setOutputCol("words")
			.setPattern("\\W+")  // Séparer les mots par des caractères non alphanumériques
			.setToLowercase(true)

		// Combiner les stop words par défaut avec les mots supplémentaires
		var stopWords = StopWordsRemover.loadDefaultStopWords("english") ++ blacklistedWords

		// Retirer les mots de la whitelist des stop words
		stopWords = stopWords.filterNot(word => whitelistedWords.contains(word))

		// Supprimer les mots vides (stop words)
		val remover = new StopWordsRemover()
			.setInputCol("words")
			.setOutputCol("filteredWords")
			.setStopWords(stopWords)

		// Filtrer les mots de une ou deux lettres et les nombres, sauf ceux de la whitelist
		val filterUselessWords = udf { words: Seq[String] =>
			words.filter(word => (word.length > 2 || whitelistedWords.contains(word)) && !word.forall(_.isDigit))
		}

		// Vectoriser les mots
		val vectorizer = new CountVectorizer()
			.setInputCol("filteredWords")
			.setOutputCol("features")

		// Créer un pipeline de traitement
		val pipeline = new Pipeline()
			.setStages(Array(tokenizer, remover, vectorizer))

		// Appliquer le pipeline sur les données
		val cleanData = pipeline.fit(data).transform(data)

		// Appliquer le filtre de mots inutiles
		val finalData = cleanData.withColumn("filteredWords", filterUselessWords(col("filteredWords")))

		finalData
	}

	// Sauvegarde le dataframe dans un fichier texte
	def saveData(data: DataFrame, path: String): Unit = {
		// Sélectionner la colonne, réduire à une partition et convertir en texte
		val textRDD = data.select("filteredWords")
			.rdd
			.coalesce(1)
			.map(row => row.getAs[Seq[String]]("filteredWords").mkString(" "))

		// Collecter les données en mémoire (attention à la taille des données)
		val textData = textRDD.collect()

		// Chemin de destination pour le fichier unique
		val outputPath = Paths.get(path + ".txt")

		// Écrire les données dans un fichier unique
		Files.write(outputPath, textData.toList.asJava, StandardOpenOption.CREATE)
	}
}
