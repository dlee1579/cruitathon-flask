import json
import plotly
import plotly.graph_objs as go


def pos_dist_plot(pos_dist):
    data = [
        go.Pie(
            labels=pos_dist["position"],
            values=pos_dist["player_id"]
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def state_dist_plot(state_dist):
    data = [
        go.Pie(
            labels=state_dist["state"],
            values=state_dist["player_id"]
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def competition_plot(comp_dist):
    # df = pd.DataFrame({'x': competitors, 'y': count_comp}) # creating a sample dataframe

    data = [
        go.Bar(
            x=comp_dist['offer'], # assign x as the dataframe column 'x'
            y=comp_dist['offer_count']
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def hometown_plot(hometown_dist):
    data = [
        go.Scattergeo(
            locationmode= 'USA-states',
            lat= hometown_dist['latitude'],
            lon= hometown_dist['longitude'],
            hoverinfo= 'text',
            text= hometown_dist['hometown'],
            marker = go.scattergeo.Marker(size=hometown_dist['h_count'])
            # size=hometown_dist['h_count']
            # marker: {
            #     size: hometown_dist['h_count'],
            #     line: {
            #         color: 'black',
            #         width: 2
            #     },
            # }
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
