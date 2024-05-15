//ETAPE 1
import org.apache.spark.sql.{SparkSession, Row}
import org.apache.spark.SparkConf
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.io._
import org.apache.spark.ml.feature.StopWordsRemover
import org.apache.spark.ml.feature.CountVectorizer
import org.apache.spark.rdd.RDD

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

    // Pour la structuration des données
    val wordsList = BookProcessor.processBooks("../data/books_large_p1.txt", spark) // ../data/books_large_p2.txt POUR CHANGER DE FICHIER

    // Arrêter la session Spark
    spark.stop()
  }
}

// Objet pour la lecture et le traitement des livres
object BookProcessor {
  def processBooks(filePath: String, spark: SparkSession): Unit = {
    // Définition du schéma du DataFrame pour lire les fichiers books_large
    val customSchema = StructType(Array(
      StructField("line", StringType, true)
    ))

    // Charger le fichier texte en un DataFrame avec une colonne "line"
    val linesDF = spark.read
      .option("header", "false")
      .schema(customSchema)
      .text(filePath)
      // .limit(100000) // A DECOCHER SI LE CODE PASSE LA PREMIERE FOIS ET SUPPRIMER LES FICHIERS GENERES

    // Ajouter une colonne avec l'indice de la ligne
    val linesWithIndexDF = linesDF.withColumn("lineIndex", monotonically_increasing_id())

    // Compter le nombre de lignes contenant "isbn"
    val countIsbn = linesWithIndexDF.filter(col("line").contains("isbn")).count()

    // Trouver les indices des lignes contenant "isbn"
    val isbnIndices = linesWithIndexDF
      .filter(col("line").contains("isbn"))
      .select("lineIndex")
      .collect()
      .map(_.getLong(0))

    // Créer des paires d'indices pour délimiter les livres
    val bookIndices = (0L +: isbnIndices).zip(isbnIndices :+ Long.MaxValue)

    // Séparer les livres en DataFrames distincts
    val bookDataFrames = bookIndices.map { case (startIndex, endIndex) =>
      linesWithIndexDF
        .filter(col("lineIndex").between(startIndex, endIndex))
        .select("line")
    }

    // Afficher tous les index
    linesWithIndexDF.select("lineIndex").show()

    // Afficher le nombre d'élements contenus dans bookDataFrames
    println(s"Nombre de livres : ${bookDataFrames.size}")

    // Afficher les premières lignes des 3 premiers livres
    bookDataFrames.take(3).zipWithIndex.foreach { case (bookDF, index) =>
      val firstLine = bookDF.first().getString(0)
      println(s"Le livre $index, première ligne : $firstLine")
    }

    // Écrire chaque livre dans un fichier séparé
    bookDataFrames.take(5).zipWithIndex.foreach { case (bookDF, index) =>
      val fileName = s"output/book_$index.txt"
      bookDF.rdd.map(_.getString(0)).toLocalIterator.grouped(1000).foreach { lines =>
        val writer = new BufferedWriter(new FileWriter(fileName, true))
        lines.foreach { line =>
          writer.write(line + "\n")
        }
        writer.close()
      }
      println(s"Le livre $index a été écrit dans $fileName")
    }
  }
}
