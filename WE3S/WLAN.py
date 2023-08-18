class WLAN:

    def __init__(self):
        self.link_capacities = [1*10**6] # AP's throughput: modulation for beacons

    def add_STA(self, link_capacity = 100 * 10**6):
        self.link_capacities.append(link_capacity)

    def set_link_capacity(self, STA_ID, link_capacity):
        assert(STA_ID < len(self.link_capacities))
        self.link_capacities[STA_ID] = link_capacity

    def get_link_capacity(self, STA_ID):
        assert(STA_ID < len(self.link_capacities))
        return self.link_capacities[STA_ID]
