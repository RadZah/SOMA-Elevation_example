# Real world example of implementation of Self-Organizing Migration Algorithm (SOMA)

This project is an example of an real workd problem implementation of a Self-Organizing Migration Algorithm.
The script tries to find the highest elevation for choosen geographic area.
It uses access to Open Topo Data or Google Elevations API (how you choose) to get the elevation data.


## Dependencies

The code relies on the following Python libraries:

- `numpy`
- `concurrent.futures`

Elevation API:

If you want to use "Google Map Elevation API", you will need API_KEY, otherwise by default the script uses "Open Topo Data API"
- optional - (`API key for Google Elevation API`) https://developers.google.com/maps/documentation/elevation/start)



## How to Run

Available parameters:
```
PATH_LENGTH = 3
STEP = 0.4
POPULATION_SIZE = 15
MIGRATIONS = 3
```

Make instance of SOMA class (with or without owns parameters)
```python
# Default parameters values
somaInstance = Soma()
# Customized parameters
somaInstance = Soma(path_length=3, step=0.11, population_size=30,migrations=4)
```

Define searched area via its coordinates:
``` python
coordinates = {
    "latt_min": 49.372811084755405,
    "latt_max": 49.67105062948057,
    "long_min": 17.94719292783253,
    "long_max": 18.541577721121097
}
somaInstance.set_area(coordinates)
```

Run the algorithm:
```
result = somaInstance.run()
```

Print results:
```
print(result)
```
Result is a dictionary with the following structure:
```
{   
    'best_elevation': 1066.926879882812,
    'best_latt': 49.47547435643843, 
    'best_long': 18.304804081775014, 
    'message': 'No change of postion during last migration',
    'no_of_migrations': 3,
    'GoogleMapAPIrequests': 25, 
    'OpenElevationAPIrequests': 0
}
```

