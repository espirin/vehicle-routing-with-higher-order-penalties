satellite_style = {
    'version': 8,
    'sources': {
        'satellite': {
            'type': 'raster',
            'tiles': [
                'https://clarity.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
            ],
            'tileSize': 512,
            'attribution': ''
        }
    },
    'layers': [
        {
            'id': 'simple-tiles',
            'type': 'raster',
            'source': 'satellite',
            'minzoom': 0,
            'maxzoom': 22
        }
    ]
}
