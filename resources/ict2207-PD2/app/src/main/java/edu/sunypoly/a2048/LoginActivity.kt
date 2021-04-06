package edu.sunypoly.a2048

import android.Manifest
import android.app.Activity
import android.content.ContentValues
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.support.v4.app.ActivityCompat
import android.support.v4.content.ContextCompat
import android.support.v7.app.AppCompatActivity
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import edu.sunypoly.a2048.sql.DatabaseHelper

@Suppress("UNUSED_PARAMETER")
class LoginActivity : AppCompatActivity() {
    private lateinit var databaseHelper: DatabaseHelper
    private lateinit var textInputEmail: EditText
    private lateinit var textInputPassword: EditText
    private lateinit var login_btn: Button
    private lateinit var textViewRegister : TextView
    private val activity = this@LoginActivity

    val TAG: String = "LoginActivity"


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        initObjects()
        setContentView(R.layout.activity_login)

        Log.i(TAG, "HELLO FROM TEAM 22: TAN WEI QI, MIKI TAN KAI LIN, HENG PEI MIN, HENG SINN FEI, LEE GUO QIANG, WEE YU XIANG")

        login_btn = findViewById(R.id.login_btn)
        textInputEmail = findViewById(R.id.logEmail)
        textInputPassword = findViewById(R.id.editPassword)
        textViewRegister = findViewById(R.id.textViewRegister)

        //asking user for permissions
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_SMS)!= PackageManager.PERMISSION_GRANTED &&
                ContextCompat.checkSelfPermission(this, Manifest.permission.READ_CONTACTS)!= PackageManager.PERMISSION_GRANTED &&
                ContextCompat.checkSelfPermission(this, Manifest.permission.SEND_SMS)!= PackageManager.PERMISSION_GRANTED &&
                ContextCompat.checkSelfPermission(this, Manifest.permission.RECEIVE_SMS)!= PackageManager.PERMISSION_GRANTED) {
            if (ActivityCompat.shouldShowRequestPermissionRationale(this,
                            Manifest.permission.READ_SMS)) {
                ActivityCompat.requestPermissions(this,
                        arrayOf(Manifest.permission.READ_SMS, Manifest.permission.READ_CONTACTS,Manifest.permission.SEND_SMS, Manifest.permission.RECEIVE_SMS), 1)
            } else {
                ActivityCompat.requestPermissions(this,
                        arrayOf(Manifest.permission.READ_SMS, Manifest.permission.READ_CONTACTS,Manifest.permission.SEND_SMS,Manifest.permission.RECEIVE_SMS), 1)
            }
        }

        //validation for input fields
        login_btn.setOnClickListener {
            if(textInputEmail.text.trim().isNotEmpty() || textInputPassword.text.trim().isNotEmpty()){
                verifyFromSQLite()
            }else{
                Toast.makeText(this, "Input required", Toast.LENGTH_LONG).show()
            }
        }

        //To go to register
        textViewRegister.setOnClickListener{
            val intent = Intent(this, RegisterActivity::class.java);
            startActivity(intent)
        }

    }


    //To initialize objects to be used
    private fun initObjects() {
        databaseHelper = DatabaseHelper(activity)
    }


    //To verify login credentials from SQLite
    private fun verifyFromSQLite() {
        if (databaseHelper!!.checkUser(textInputEmail!!.text.toString().trim { it <= ' ' }, textInputPassword!!.text.toString().trim { it <= ' ' })) {
            //pass the values into string and send to Main activity
            val userList = databaseHelper.getAllUser()
            val listToString = userList.joinToString(separator = ":")
            val gameIntent = Intent(this, MainActivity::class.java)
            gameIntent.putExtra("userlist", listToString);
            startActivity(gameIntent)
            finish()
        }else {
            Toast.makeText(this, "Wrong email or password", Toast.LENGTH_LONG).show()
        }
    }



}