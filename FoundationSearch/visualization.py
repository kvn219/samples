from highcharts import Highchart

options = {
	'chart': {
        'type': 'scatter',
        'zoomType': 'xy'
    },
    'title': {
        'text': 'What does your following look like?'
    },
    'subtitle': {
        'text': "Plotting twitter friends and followers on a logarithmic scale"
    },
    'xAxis': {
        'type': 'logarithmic',
        'title': {
            'enabled': True,
            'text': 'Num of Followers'
        },
        'startOnTick': True,
        'endOnTick': True,
        'showLastLabel': True
    },
    'yAxis': {
        'type': 'logarithmic',
        'title': {
            'text': 'Num of Friends'
        }
    },
    'legend': {
        'layout': 'vertical',
        'align': 'left',
        'verticalAlign': 'top',
        'x': 100,
        'y': 70,
        'floating': True,
        'backgroundColor': "(Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'",
        'borderWidth': 1
    },
    'plotOptions': {
        'scatter': {
            'marker': {
                'radius': 5,
                'states': {
                    'hover': {
                        'enabled': True,
                        'lineColor': 'rgb(100,100,100)'
                    }
                }
            },
            'states': {
                'hover': {
                    'marker': {
                        'enabled': False
                    }
                }
            },
            'tooltip': {
                'headerFormat': '<b>{series.name} Social Media Following</b><br>',
                'pointFormat': 'Followers: {point.x}<br>Friends: {point.y}',
                },
        },
    },
}
