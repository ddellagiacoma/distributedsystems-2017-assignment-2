curl -d 'entry=ciao8' -X 'POST' 'http://10.1.0.8:80/board' & 
curl -d 'entry=ciao5' -X 'POST' 'http://10.1.0.5:80/board' & 
curl -d 'entry=ciao1' -X 'POST' 'http://10.1.0.1:80/board'
