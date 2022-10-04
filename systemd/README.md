sudo ln -s /home/pi/repos/beton-in-form-crawler/systemd/beton-in-form-crawler.service /etc/systemd/system/beton-in-form-crawler.service
sudo systemctl daemon-reload
sudo systemctl enable beton-in-form-crawler
sudo systemctl start beton-in-form-crawler
