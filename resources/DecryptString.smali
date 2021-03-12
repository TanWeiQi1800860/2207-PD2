.class public Lcom/DecryptManager/DecryptString/DecryptString;
.super Ljava/lang/Object;
.source "DecryptString.java"

# static fields
.field private static final initVector:Ljava/lang/String; = "0000000000000000"

.field private static secret:Ljava/lang/String;


# direct methods
.method static constructor <clinit>()V
    .locals 1

    .line 16
    const-string v0, "Thereisnospoon68"

    sput-object v0, Lcom/DecryptManager/DecryptString/DecryptString;->secret:Ljava/lang/String;

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .line 14
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static decrypt(Ljava/lang/String;)Ljava/lang/String;
    .locals 6
    .param p0, "encrypted"    # Ljava/lang/String;

    .line 22
    const-string v0, "UTF-8"

    :try_start_0
    new-instance v1, Ljavax/crypto/spec/IvParameterSpec;

    const-string v2, "0000000000000000"

    invoke-virtual {v2, v0}, Ljava/lang/String;->getBytes(Ljava/lang/String;)[B

    move-result-object v2

    invoke-direct {v1, v2}, Ljavax/crypto/spec/IvParameterSpec;-><init>([B)V

    .line 23
    .local v1, "iv":Ljavax/crypto/spec/IvParameterSpec;
    new-instance v2, Ljavax/crypto/spec/SecretKeySpec;

    sget-object v3, Lcom/DecryptManager/DecryptString/DecryptString;->secret:Ljava/lang/String;

    invoke-virtual {v3, v0}, Ljava/lang/String;->getBytes(Ljava/lang/String;)[B

    move-result-object v0

    const-string v3, "AES"

    invoke-direct {v2, v0, v3}, Ljavax/crypto/spec/SecretKeySpec;-><init>([BLjava/lang/String;)V

    move-object v0, v2

    .line 25
    .local v0, "skeySpec":Ljavax/crypto/spec/SecretKeySpec;
    const-string v2, "AES/CBC/PKCS5PADDING"

    invoke-static {v2}, Ljavax/crypto/Cipher;->getInstance(Ljava/lang/String;)Ljavax/crypto/Cipher;

    move-result-object v2

    .line 26
    .local v2, "cipher":Ljavax/crypto/Cipher;
    const/4 v3, 0x2

    invoke-virtual {v2, v3, v0, v1}, Ljavax/crypto/Cipher;->init(ILjava/security/Key;Ljava/security/spec/AlgorithmParameterSpec;)V

    .line 27
    const/4 v3, 0x0

    invoke-static {p0, v3}, Landroid/util/Base64;->decode(Ljava/lang/String;I)[B

    move-result-object v3

    invoke-virtual {v2, v3}, Ljavax/crypto/Cipher;->doFinal([B)[B

    move-result-object v3

    .line 28
    .local v3, "original":[B
    const-string v4, "Decrypt"

    new-instance v5, Ljava/lang/String;

    invoke-direct {v5, v3}, Ljava/lang/String;-><init>([B)V

    invoke-static {v4, v5}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 29
    new-instance v4, Ljava/lang/String;

    invoke-direct {v4, v3}, Ljava/lang/String;-><init>([B)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    return-object v4

    .line 30
    .end local v0    # "skeySpec":Ljavax/crypto/spec/SecretKeySpec;
    .end local v1    # "iv":Ljavax/crypto/spec/IvParameterSpec;
    .end local v2    # "cipher":Ljavax/crypto/Cipher;
    .end local v3    # "original":[B
    :catch_0
    move-exception v0

    .line 31
    .local v0, "ex":Ljava/lang/Exception;
    invoke-virtual {v0}, Ljava/lang/Exception;->printStackTrace()V

    .line 33
    .end local v0    # "ex":Ljava/lang/Exception;
    const/4 v0, 0x0

    return-object v0
.end method
