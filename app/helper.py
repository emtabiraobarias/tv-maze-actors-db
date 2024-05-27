import requests
import numpy as np
import pandas as pd
import io
from model import Actor, Show
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

class TVMaze_API_Access:
    def __init__(self, url):
        self.url = url

    def get_json(self, url):
        resp = requests.get(url=url)
        data = resp.json()
        return data

    def get_actor(self, name) -> Actor:
        query_url = self.url + name
        print(query_url)
        # Fetch the query result to a json object
        json_obj = self.get_json(query_url)
        # Ensure the highest scored actor response exactly matches the queried actor name
        if str(json_obj[0]['person']['name']).lower() == name.lower():
            # Retrieve shows for the current actor
            shows_query_url = 'https://api.tvmaze.com/people/{}/castcredits'.format(json_obj[0]['person']['id'])
            shows_json_obj = self.get_json(shows_query_url)
            show_urls = map(lambda n: n['_links']['show']['href'], shows_json_obj)
            show_details = map(lambda n: self.get_json(n), show_urls)
            show_names = map(lambda n: n['name'], show_details)
            show_entities = []
            for show_name in show_names:
                existing_show = Show.find_by_showname(show_name)
                if existing_show is None:
                    show_entities.append(Show(name = show_name))
                else:
                    show_entities.append(existing_show)
            actor = Actor.from_json(json_obj[0]['person'])
            actor.shows = show_entities
            return actor
        else: 
            return None


class Statistics_Helper:

    @staticmethod
    def build_group_dict(df_aggregate, group_by_dict, by_attr):
        for key in df_aggregate.index:
            group_by_attr = {} if group_by_dict.get(by_attr) is None else group_by_dict.get(by_attr)
            group_by_attr[key] = df_aggregate[key]
            group_by_dict[by_attr] = group_by_attr
        return group_by_dict

    # Circular bar chart customisation copied from: https://python-graph-gallery.com/circular-barplot-with-groups
    @classmethod
    def add_labels(cls, angles, values, labels, offset, ax):
        
        # This is the space between the end of the bar and the label
        padding = 4
        
        # Iterate over angles, values, and labels, to add all of them.
        for angle, value, label, in zip(angles, values, labels):
            angle = angle
            
            # Obtain text rotation and alignment
            rotation, alignment = cls.get_label_rotation(angle, offset)

            # And finally add the text
            ax.text(
                x=angle, 
                y=value + padding, 
                s=label, # + ' (' + str(value) + '%)', 
                ha=alignment, 
                va="center", 
                rotation=rotation, 
                rotation_mode="anchor"
            ) 

    # Circular bar chart customisation copied  from: https://python-graph-gallery.com/circular-barplot-with-groups
    @classmethod
    def get_label_rotation(cls, angle, offset):
        # Rotation must be specified in degrees :(
        rotation = np.rad2deg(angle + offset)
        if angle <= np.pi:
            alignment = "right"
            rotation = rotation + 180
        else: 
            alignment = "left"
        return rotation, alignment

    # Circular bar chart customisation based from: https://python-graph-gallery.com/circular-barplot-with-groups
    @classmethod
    def generate_viz(cls, group_by_dict):
        categories = list(group_by_dict.keys())
        names = []
        values = []
        groups = []
        GROUPS_SIZE = []
        for category in categories:
            group_category = group_by_dict[category]
            names = names + list(group_category.keys())
            values = values + list(group_category.values())
            groups = groups + ([category] * len(group_category))
            GROUPS_SIZE.append(len(group_category))
            
        # Determines where to place the first bar. 
        # By default, matplotlib starts at 0 (the first bar is horizontal)
        # but here we say we want to start at pi/2 (90 deg)
        OFFSET = np.pi / 2

        # Build a dataset
        df = pd.DataFrame({
            "name": names, 
            "value": values,
            "group": groups 
        })

        # All this part is like the code above
        VALUES = df["value"].values
        LABELS = df["name"].values
        GROUP = df["group"].values

        PAD = 3
        ANGLES_N = len(VALUES) + PAD * len(np.unique(GROUP))
        ANGLES = np.linspace(0, 2 * np.pi, num=ANGLES_N, endpoint=False)
        WIDTH = (2 * np.pi) / len(ANGLES)

        offset = 0
        IDXS = []
        for size in GROUPS_SIZE:
            IDXS += list(range(offset + PAD, offset + size + PAD))
            offset += size + PAD

        plt.switch_backend('agg') # fix for issue caused by generating plot from REST call
        fig, ax = plt.subplots(figsize=(20, 10), subplot_kw={"projection": "polar"})
        ax.set_theta_offset(OFFSET)
        ax.set_ylim(-100, 100)
        ax.set_frame_on(False)
        ax.xaxis.grid(False)
        ax.yaxis.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])

        COLORS = [f"C{i}" for i, size in enumerate(GROUPS_SIZE) for _ in range(size)]

        ax.bar(
            ANGLES[IDXS], VALUES, width=WIDTH, color=COLORS,
            edgecolor="white", linewidth=2
        )

        cls.add_labels(ANGLES[IDXS], VALUES, LABELS, OFFSET, ax)

        # This iterates over the sizes of the groups adding reference
        # lines and annotations.
        offset = 0 
        for group, size in zip(categories, GROUPS_SIZE):
            # Add line below bars
            x1 = np.linspace(ANGLES[offset + PAD], ANGLES[offset + size + PAD - 1], num=50)
            ax.plot(x1, [-5] * 50, color="#333333")
            
            # Add text to indicate group
            ax.text(
                np.mean(x1), -20, group, color="#333333", fontsize=14, 
                fontweight="bold", ha="center", va="center"
            )
            
            # Add reference lines at 20, 40, 60, and 80
            x2 = np.linspace(ANGLES[offset], ANGLES[offset + PAD - 1], num=50)
            ax.plot(x2, [20] * 50, color="#bebebe", lw=0.8)
            ax.plot(x2, [40] * 50, color="#bebebe", lw=0.8)
            ax.plot(x2, [60] * 50, color="#bebebe", lw=0.8)
            ax.plot(x2, [80] * 50, color="#bebebe", lw=0.8)
            
            offset += size + PAD

        fig.suptitle('Actor Statistics', fontsize=20)
        return fig
    
    @staticmethod
    def generate_viz_image(group_by_dict: dict) -> io.BytesIO: 
        # generate visualisation (stacked charts)
        chart_fig = Statistics_Helper.generate_viz(group_by_dict)
        output = io.BytesIO()
        FigureCanvas(chart_fig).print_png(output)
        return output
    
    @staticmethod
    def generate_stats_json(total_actors: int, total_updated: int, group_by_dict: dict) -> dict:
        #merge the dictionaries in one for single return json
        total_dict = {
            'total': total_actors,
            'total-updated': total_updated
        }
        return_json = {**total_dict, **group_by_dict}
        return return_json