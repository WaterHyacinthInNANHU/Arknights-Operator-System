修改application.yml中的配置

## TO DO List
- [x] 登陆(目前使用sa-token cookie方案 后续可以使用token)
- [x] 注册(目前使用httpsession+cookies存邮件验证码，后续可以使用redis)
- [ ] 修改部分代码为post
- [x] 改密码(发送邮件也许可以和注册合并一下？)
- [ ] 美化注册邮件
- [ ] 了解event stream
- [ ] 全局异常处理



Server part
This part is developed by qxdn
<pre>
\\ \\ \\ \\ \\ \\ \\ \\ || || || || || || // // // // // // // //
\\ \\ \\ \\ \\ \\ \\        _ooOoo_          // // // // // // //
\\ \\ \\ \\ \\ \\          o8888888o            // // // // // //
\\ \\ \\ \\ \\             88" . "88               // // // // //
\\ \\ \\ \\                (| -_- |)                  // // // //
\\ \\ \\                   O\  =  /O                     // // //
\\ \\                   ____/`---'\____                     // //
\\                    .'  \\|     |//  `.                      //
==                   /  \\|||  :  |||//  \                     ==
==                  /  _||||| -:- |||||-  \                    ==
==                  |   | \\\  -  /// |   |                    ==
==                  | \_|  ''\---/''  |   |                    ==
==                  \  .-\__  `-`  ___/-. /                    ==
==                ___`. .'  /--.--\  `. . ___                  ==
==              ."" '<  `.___\_<|>_/___.'  >'"".               ==
==            | | :  `- \`.;`\ _ /`;.`/ - ` : | |              \\
//            \  \ `-.   \_ __\ /__ _/   .-` /  /              \\
//      ========`-.____`-.___\_____/___.-`____.-'========      \\
//                           `=---='                           \\
// //   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  \\ \\
// // //      佛祖保佑      永无BUG      永不修改        \\ \\ \\
// // // // // // || || || || || || || || || || \\ \\ \\ \\ \\ \\
</pre>