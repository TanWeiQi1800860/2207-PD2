package edu.sunypoly.a2048

import android.content.ContentValues
import android.content.Intent
import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import edu.sunypoly.a2048.modal.User
import edu.sunypoly.a2048.sql.DatabaseHelper
import java.util.regex.Pattern

@Suppress("UNUSED_PARAMETER")
class RegisterActivity : AppCompatActivity() {
    private val activity = this@RegisterActivity
    private lateinit var databaseHelper: DatabaseHelper
    private lateinit var textInputEmail: EditText
    private lateinit var textInputPassword: EditText
    private lateinit var textInputCPassword: EditText
    private lateinit var reg_btn: Button
    private lateinit var textViewLogin : TextView

    override fun onCreate(savedInstanceState: Bundle?){
        super.onCreate(savedInstanceState)
        initObjects()
        setContentView(R.layout.activity_register)

        textInputEmail = findViewById(R.id.regEmail)
        textInputPassword = findViewById(R.id.regPwd)
        textInputCPassword = findViewById(R.id.regCPwd)
        reg_btn = findViewById(R.id.reg_btn)
        textViewLogin = findViewById(R.id.textViewLogin)

        val EMAIL_ADDRESS_PATTERN: Pattern = Pattern.compile(
                "[a-zA-Z0-9+.%-+]{1,256}" +
                        "@" +
                        "[a-zA-Z0-9][a-zA-Z0-9-]{0,64}" +
                        "(" +
                        "." +
                        "[a-zA-Z0-9][a-zA-Z0-9-]{0,25}" +
                        ")+"
        )

        //validation for input fields
        reg_btn.setOnClickListener{
            if(textInputEmail.text.isEmpty() || textInputCPassword.text.isEmpty() || textInputPassword.text.isEmpty()){
                Toast.makeText(this, "Input Required", Toast.LENGTH_LONG).show()
            }
            if(!EMAIL_ADDRESS_PATTERN.matcher(textInputEmail.text.toString()).matches()){
                Toast.makeText(this,"Invalid Email Address",Toast.LENGTH_SHORT).show();
            }
            else if(!textInputPassword.text.toString().equals(textInputCPassword.text.toString())){
                Toast.makeText(this,"Password Not Match",Toast.LENGTH_SHORT).show();
            }
            else{
                postDataToSQLite()
            }
        }

        //To go to login
        textViewLogin.setOnClickListener{
            val intent = Intent(this, LoginActivity::class.java);
            startActivity(intent);
        }



    }

    //To initialize objects to be use
    private fun initObjects() {
        databaseHelper = DatabaseHelper(activity)
    }

    //To check user and post data to SQLite
    private fun postDataToSQLite() {
        if (!databaseHelper!!.checkUser(textInputEmail!!.text.toString().trim())) {
            var user = User(email = textInputEmail!!.text.toString().trim(),
                    password = textInputPassword!!.text.toString().trim())
            databaseHelper!!.addUser(user)
            Toast.makeText(this, "Registered successfully.", Toast.LENGTH_LONG).show()
            finish()
        } else {
            Toast.makeText(this, "Record already registered", Toast.LENGTH_LONG).show()
        }
    }

}