from typing import List
from crawler import Crawler, UrlFilterer
from scorer import core_web_score
import networkx as nx
import matplotlib.pyplot as plt
from time import perf_counter


class Wikid:
    BASE_URL = 'https://en.wikipedia.org/wiki/'

    def __init__(
        self, 
        start_url: str, 
        dest_url: str,
        start_alias: str = None,
        dest_alias: str = None,
        interests: List[str] = [],
        amount_of_matching_urls: int = 25,
    ):
        self.amount_of_matching_urls = amount_of_matching_urls
        
        self.start_url = start_url
        self.start_alias = start_alias

        self.dest_url = dest_url
        self.dest_alias = dest_alias

        self.interests = interests

        self.path = None
        self.visited = set()
        self.graph = nx.DiGraph()
        self.crawler = Crawler(
            filter_url=UrlFilterer(
                allowed_domains={"en.wikipedia.org"},
                allowed_schemes={"https"},
                allowed_filetypes={""},
                additional_filters={lambda x: ":" not in x.split(Wikid.BASE_URL)[-1]}
            ).filter_url,
        )

    def article_from_url(self, url: str):
        if self.start_alias and url is self.start_url:
            return self.start_alias
        if self.dest_alias and url is self.dest_url:
            return self.dest_alias
        return url.split("/")[-1]

    def get_links(self, url: str):
        link_scores = []
        for link in self.crawler.crawl(url):
            
            score = core_web_score(
                self.article_from_url(link),
                self.article_from_url(self.dest_url),
                user_interests=self.interests
            )
            if link == self.dest_url: return [(link, score)]
            # print(link, self.dest_url, score)
            link_scores.append((link, score))
        return sorted(link_scores, key=lambda x: x[1], reverse=True)[:self.amount_of_matching_urls]

    def get_heaviest_unchecked_link(self):
        best_weight = 0
        best_url = None
        for _, url, data in self.graph.edges(data=True):
            if url in self.visited:
                continue
            if data["weight"] >= best_weight:
                best_weight = data["weight"]
                best_url = url
            
        return best_url, best_weight

    def add_links_to_graph(self, url: str):
        self.visited.add(url)
        for link, score in self.get_links(url):
            if link in self.visited or link == url:
                continue
            self.graph.add_edge(url, link, weight=score)
            if link == self.dest_url:
                return link
        url, _ = self.get_heaviest_unchecked_link()
        print("Checking", url, _)
        self.add_links_to_graph(url)

    def show_graph(self, desired_layout=nx.spiral_layout):
        # create labels dictionary for nodes in shortest path
        labels = {node: self.article_from_url(node) if node in self.path else "" for node in self.graph.nodes()}

        # create edge and node colors based on whether they are in the shortest path
        edge_colors = ["red" if (u, v) in zip(self.path, self.path[1:]) else "gray" for u, v in self.graph.edges()]
        node_colors = ["red" if node in self.path else "gray" for node in self.graph.nodes()]

        # draw the graph with customized edge and node colors, thickness, opacity, and size
        pos = desired_layout(self.graph)
        nx.draw_networkx_edges(
            self.graph, 
            pos, 
            edgelist=self.graph.edges(), 
            edge_color=edge_colors, 
            width=[3 if (u, v) in zip(self.path, self.path[1:]) else 1 for u, v in self.graph.edges()], 
            alpha=0.5
        )
        nx.draw_networkx_nodes(
            self.graph, pos, 
            node_color=node_colors, 
            node_size=[800 if node in self.path else 200 for node in self.graph.nodes()], 
            alpha=0.5
        )
        nx.draw_networkx_labels(self.graph, pos, labels)

        # display the graph
        plt.show()     

    def run(self):
        self.add_links_to_graph(self.start_url)

        self.path = nx.shortest_path(self.graph, source=self.start_url, target=self.dest_url, weight='score')

        return self.path

def main():
    wikid = Wikid(
        "https://en.wikipedia.org/wiki/Camping", 
        "https://en.wikipedia.org/wiki/Depression_(mood)",
        amount_of_matching_urls=5,
        dest_alias="depressed"
    )
    path = wikid.run()
    wikid.show_graph()
    print(path)

if __name__ == '__main__':
    print("Starting...")
    start = perf_counter()
    main()
    end = perf_counter() - start
    print("Total Time: ", end)


