# data initialization and get data from direction
import os, sys, dgl, pickle, random
import torch as th
from dgl.data import DGLDataset


class iCallds2(DGLDataset):
    directory = '/home/isec/Documents/differentopdata/Reorganized_Dataset/zenodo/graph/graph_dir_70_random' ##"E:\\iCallds
    numgraph = 1507
    revedge = True
    calledges = True
    laplacian_pe = True
    adddata = True
    addfunc = True
    dataRefedgs = True
    codeRefedgs = True
    onlySave = False
    def __init__(self, Revedges = True, Calledges=True, Laplacian_pe=False,
                 Adddata = True, Addfunc = True, DataRefedgs = True, CodeRefedgs = True, Onlysave = False):#
        super().__init__(name='iCalls')
        self.revedge = Revedges
        self.calledges = Calledges
        self.laplacian_pe = Laplacian_pe
        self.adddata = Adddata
        self.addfunc = Addfunc
        self.dataRefedgs = DataRefedgs
        self.codeRefedgs = CodeRefedgs
        self.onlySave = Onlysave

    def process(self):
        return


    def __getitem__(self, i):
        #i = '0303db951e1cc967eb1086fafda39e97a6b33158bf57a6aef8f25b02d7a29103'
        #i = 0
        graphfile = os.path.join(self.directory, str(i)+'.graph')
        glist, glabel = dgl.data.utils.load_graphs(graphfile)

        funcaddrfile = os.path.join(self.directory, str(i) + '.funcaddr')
        with open(funcaddrfile, 'rb') as fp:
            savefunc = pickle.load(fp)

        if self.laplacian_pe:
            graphfile = os.path.join(self.directory, str(i) + '.graphpe')
            if os.path.exists(graphfile):
                print(i)
                glist, _ = dgl.data.utils.load_graphs(graphfile)
                if self.onlySave:
                    return glist, glabel
            else:
                g = dgl.to_homogeneous(glist[0], store_type=False, return_count=False)
                pe = dgl.laplacian_pe(g, 2)
                nowi = 0
                for i in glist[0].ntypes:
                    if i == 'func':
                        glist[0].nodes[i].data['feat'] = pe[nowi:nowi + glist[0].num_nodes(i)]
                    else:
                        glist[0].nodes[i].data['feat'] = th.cat(
                        (pe[nowi:nowi + glist[0].num_nodes(i)], glist[0].nodes[i].data['feat']), dim=1)
                    nowi += glist[0].num_nodes(i)

                dgl.data.utils.save_graphs(graphfile, glist, glabel)
                if self.onlySave:
                    return glist, glabel

        fcalllist = {}
        calllist = {}

        '''
        for i in range(len(glist[0].edges(etype='GT_edges')[0])):
            if glist[0].edges(etype='GT_edges')[0][i].item() not in calllist:
                calllist[glist[0].edges(etype='GT_edges')[0][i].item()] = []
                fcalllist[glist[0].edges(etype='GT_edges')[0][i].item()] = []
            calllist[glist[0].edges(etype='GT_edges')[0][i].item()].append(glist[0].edges(etype='GT_edges')[1][i].item())
        '''
        glabel['GT_label'] = glabel['GT_label'].T
        for i in range(len(glabel['GT_label'][0])):
            if glabel['GT_label'][0][i].item() not in calllist:
                calllist[glabel['GT_label'][0][i].item()] = []
            calllist[glabel['GT_label'][0][i].item()].append(glabel['GT_label'][1][i].item())

        funcaddrs = list(savefunc.values())
        limit = glist[0].num_nodes("code")
        funcaddrs = [num for num in funcaddrs if num < limit]


        #GT_F_edges = []
        GT_F_edges_s = []
        GT_F_edges_d = []
        funcaddrs_sum = list(set(val for values in calllist.values() for val in values)) # added 11/09/2024
        old_funcaddrs = funcaddrs.copy()
        for key, value in calllist.items():
            funcaddrs = [item for item in funcaddrs_sum if item not in value] #added for debuging 11/09/2024
            for _ in range(len(value)):
                if not funcaddrs:
                    funcaddrs = old_funcaddrs
                if not old_funcaddrs:
                    break
                r = random.choice(funcaddrs)
                funcaddrs.remove(r)
                GT_F_edges_s.append(key)
                GT_F_edges_d.append(r)

        if not self.calledges:
            tmp = glist[0].edges(etype='codecall_edges')
            glist[0] = dgl.add_edges(glist[0], tmp[0], tmp[1], etype='code2code_edges')
            # glist[0] = dgl.remove_edges(glist[0], range(glist[0].num_edges(('code', 'codecall_edges', 'code'))), ('code', 'codecall_edges', 'code'))
        rel_names = [('code', 'code2func_edges', 'func'),
                     ('code', 'code2code_edges', 'code'),
                     ('code', 'codecall_edges', 'code'),
                     ('code', 'codexrefcode_edges', 'code'),
                     ('code', 'codexrefdata_edges', 'data'),
                     ('data', 'dataxrefcode_edges', 'code'),
                     ('data', 'dataxrefdata_edges', 'data')
                     ]
        if not self.adddata:
            rel_names = [o for o in rel_names if o[0] != 'data' and o[2] != 'data']
        if not  self.addfunc:
            rel_names = [o for o in rel_names if o[0] != 'func' and o[2] != 'func']
        if not  self.dataRefedgs:
            rel_names = [o for o in rel_names if not o[1].endswith('xrefdata_edges')]
        if not  self.codeRefedgs:
            rel_names = [o for o in rel_names if not o[1].endswith('xrefcode_edges')]
        if not  self.calledges:
            rel_names = [o for o in rel_names if not o[1].endswith('codecall_edges')]
        glist[0] = glist[0].edge_type_subgraph(rel_names)
        if self.adddata:
            if not self.addfunc:
                glist[0] = glist[0].node_type_subgraph(['code', 'data'])
        else:
            if self.addfunc:
                glist[0] = glist[0].node_type_subgraph(['code', 'func'])
            else:
                glist[0] = glist[0].node_type_subgraph(['code'])
        #if not self.dataRefedgs:
        #    glist[0] = dgl.remove_edges(glist[0], range(glist[0].num_edges(('code', 'codexrefdata_edges', 'data'))), ('code', 'codexrefdata_edges', 'data'))
        #    glist[0] = dgl.remove_edges(glist[0], range(glist[0].num_edges(('data', 'dataxrefdata_edges', 'data'))), ('data', 'dataxrefdata_edges', 'data'))
        #if not self.codeRefedgs:
        #    glist[0] = dgl.remove_edges(glist[0], range(glist[0].num_edges(('code', 'codexrefcode_edges', 'code'))), ('code', 'codexrefcode_edges', 'code'))
        #    glist[0] = dgl.remove_edges(glist[0], range(glist[0].num_edges(('data', 'dataxrefcode_edges', 'code'))), ('data', 'dataxrefcode_edges', 'code'))
        if self.revedge:
            AddReverse = dgl.transforms.AddReverse(sym_new_etype=True)
            glist[0] = AddReverse(glist[0])
        return glist[0], {'GT_edges': glabel['GT_label'], 'GT_F_edges': th.tensor([GT_F_edges_s, GT_F_edges_d])}

    def __len__(self):
        return self.numgraph


'''if __name__ == "__main__":
    dataset = iCallds2(Calledges=False, Adddata=False, Laplacian_pe=True)
    g, glabels = dataset[0]'''