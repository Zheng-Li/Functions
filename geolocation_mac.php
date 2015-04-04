<?php

	function  geo_lookup($address, $KEY) {
		$address = str_replace (" ", "+", urlencode($address));
  		$geo_url = "https://maps.googleapis.com/maps/api/geocode/json?sensor=false&address=".$address; 
   		$ch = curl_init();
   		curl_setopt($ch, CURLOPT_URL, $geo_url);
   		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
   		$response = json_decode(curl_exec($ch), true);
 		   // If Status Code is ZERO_RESULTS, OVER_QUERY_LIMIT, REQUEST_DENIED or INVALID_REQUEST
   		if ($response['status'] != 'OK') {
   			print_r($response);
    		return null;
   		}

   		$geometry = $response['results'][0]['geometry'];
 
    	$longitude = $geometry['location']['lat'];
    	$latitude = $geometry['location']['lng'];
 
    	$array = array(
        	'latitude' => $geometry['location']['lng'],
        	'longitude' => $geometry['location']['lat'],
        	'location_type' => $geometry['location_type'],
    	);
 
    	return $array;
	}

$address = 'Salt Lake City, Utah';
$KEY = 'AIzaSyDbpr1vmkIjy3PKfYtDAwQTdzj4tR-KDgU';
$array = geo_lookup($address, $KEY);
if($array) {
	print_r($array);
} else {
	echo "fjdksla;fjkdsla";
}

?>