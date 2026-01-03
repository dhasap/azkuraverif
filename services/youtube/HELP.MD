Link YouTube sedikit berbeda, mirip dengan https://offers.sheerid.com/youtube/student/?yrdup=https%3A%2F%2Fwww.youtube.com%2F%3Fsld%3Dxxxxxxxxxxxxxxxytpid=premium&ytsku=premium&yrsp=https%3A%2F%2Fwww.youtube.com%2Fpremium%2FstudxxxxxxxxxxxxQQBRgO&euid=230493635&locale=en-US&oid=AI97cxxxxxxxxxxxxxxxxxxxxxNT06Nb5kDzo384b8cAu

Tidak ada informasi programId dan verificationId SheerID, jadi Anda perlu capture interface sendiri

Buka network log dan cari `https://services.sheerid.com/rest/v2/verification/`
Dapatkan programId dari payload dan verificationId dari response

Buat link secara manual
https://services.sheerid.com/verify/xxxxxxxxxx/?verificationId=yyyyyyyyyyy
Di sini xxx adalah programId
yyyy adalah verificationId