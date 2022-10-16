# beton-in-form-crawler

My wife wants to order stuff from a popular web shop, that is closed most of the time because of heavy demand. So I wrote a web crawler that notifies her in case the shop opens. It periodically checks if it can put an item into the shopping card. If it succeeds (i.e. shop is open) it sends out an email.

The crawler runs as a systemd service on my home server (raspberry pi).
