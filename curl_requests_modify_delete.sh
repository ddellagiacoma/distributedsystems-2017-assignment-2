curl -d 'entry=ciaoNew1&delete=0' -X 'POST' 'http://10.1.0.8:80/board/1' & 
curl -d 'entry=ciao5&delete=1' -X 'POST' 'http://10.1.0.5:80/board/2' & 
curl -d 'entry=ciaoNew3&delete=0' -X 'POST' 'http://10.1.0.1:80/board/3'
