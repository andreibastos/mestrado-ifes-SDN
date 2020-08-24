from mininet.topo import Topo

class FatTreeTopo(Topo):
    """
    Parameters
    ----------
    k : int
        Ports per switch
    """

    def __init__(self, k=4):
        # Initialize topology
        Topo.__init__(self)
        self.k = k

        core = self.core()
        for n in range(k):
            pod = self.pod(n)
            self.link_pod_core(pod, core)
        

    def link_pod_core(self, pod, core):
        aggregations = pod['aggregations']
        size = len(aggregations)
        for index, aggregation in enumerate(aggregations):
            if index < size / 2:
                core_half = core[0:len(core)/2]
            else:
                core_half = core[len(core)/2:]
            for c in core_half:
                self.addLink(aggregation, c)

    def pod(self, pod_n):
        aggregations = self.aggregation(pod_n)
        edges = self.edge(pod_n)

        pod = {'aggregations': aggregations, 'edges': edges}

        for switch in aggregations:
            for edge in edges:                
                self.addLink(switch, edge)

        for index, switch in enumerate(edges):
            hosts = ['h_%s_%s' %
                     (pod_n+1, pod_n*self.k + index*2+h+1) for h in range(2)]
            for host in hosts:
                self.addHost(host)
                self.addLink(switch, host)
        print '\n'
        return pod

    def core(self):
        return self.list_switches(self.k, 's_c_')

    def aggregation(self, pod):
        return self.list_switches(self.k/2, 's_%s_a_' % pod)

    def edge(self, pod):
        return self.list_switches(self.k, 's_%s_e_' % pod)

    def list_switches(self, k, prefix):
        switches = []
        for s in range(k):
            switch = '%s%s' % (prefix, s)
            self.addSwitch(switch)
            switches.append(switch)
        return switches
