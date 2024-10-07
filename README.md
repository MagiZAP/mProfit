# mProfit Magi - Magi all in one Calculator
**This is a Magi (XMG) mining and staking (mPoW/mPoS) calculator.**

---

### HOW TO USE:

You can use the calculator on [MagiZAP website](https://www.magizap.com/mprofit) or you can download UI.html file and open it for example in your browser. 

UI.html files are connected to mProfit Host (mp.magizap.com:443) by default.

Feel free to use `https://mp.magizap.com:443` as a server for your calculator.

---

### HOW TO SETUP YOUR OWN HOST SERVER:

- #### Download latest release, extract and edit following lines in # SETTINGS in mProfit.py:

  magi_rpc_user = `'user'` <-- Your RPC username in magi.conf.

  magi_rpc_password = `'pass'` <-- Your RPC password in magi.conf.

  magi_rpc_ip = `'localhost'` <-- IP address of the RPC host. (localhost = 127.0.0.1)

  magi_rpc_port = `'8232'` <-- Port of the RPC host in magi.conf.

  host_ip = `'0.0.0.0'` <-- IP address that you want to host on. (0.0.0.0 = all IP)

  host_port = `443` <-- Port that you want to host on. (443 is the main port for HTTPS)

  allowed_origins = `'*'` <-- Allowed IP addresses that can connect to your server to use the calculator.

  pem_file_location = `'file.pem'` <-- SSL/TLS certificate file location. (needed only for HTTPS connection)

  key_file_location = `'file.key'` <-- SSL/TLS private key file location. (needed only for HTTPS connection)

  periodic_reset_timing = `60` <-- How often to refresh the server to avoid errors in seconds. (server can sometimes get stuck)

  time_between_requests = `3` <-- Time that must pass in order to accept new request in seconds. (spam prevention)

- #### Edit/create your UI for example in HTML:

  Edit or add URL/IP of your server:

  `fetch('https://mp.magizap.com:443/calculate/mining', ...` (example)

- #### Make your calculator public:

  If you have static public IP address, you can use port forwarding between your local server IP and the public IP address.

  If you also have a domain, then you can assign this IP to it through DNS record.

---

Made by [MagiZAP](https://www.magizap.com) - XMG multi-tool website.

XMG donation address: `976Q8kRwiRGcMsKgoHVAgAagCXMpE2NsZ1`
