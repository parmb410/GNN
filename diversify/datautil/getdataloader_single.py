# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import numpy as np
import torch
from torch.utils.data import DataLoader

import datautil.actdata.util as actutil
from datautil.util import combindataset, subdataset
import datautil.actdata.cross_people as cross_people

task_act = {
    'cross_people': cross_people,
}


def get_dataloader(args, tr, val, tar):
    train_loader = DataLoader(
        dataset=tr,
        batch_size=args.batch_size,
        num_workers=args.N_WORKERS,
        drop_last=False,
        shuffle=True
    )
    train_loader_noshuffle = DataLoader(
        dataset=tr,
        batch_size=args.batch_size,
        num_workers=args.N_WORKERS,
        drop_last=False,
        shuffle=False
    )
    valid_loader = DataLoader(
        dataset=val,
        batch_size=args.batch_size,
        num_workers=args.N_WORKERS,
        drop_last=False,
        shuffle=False
    )
    target_loader = DataLoader(
        dataset=tar,
        batch_size=args.batch_size,
        num_workers=args.N_WORKERS,
        drop_last=False,
        shuffle=False
    )
    return train_loader, train_loader_noshuffle, valid_loader, target_loader


def get_act_dataloader(args):
    if not hasattr(args, 'N_WORKERS'):
        args.N_WORKERS = 4

    args.steps_per_epoch = float('inf')

    source_datasetlist = []
    target_datalist = []

    pcross_act = task_act[args.task]
    tmpp = args.act_people[args.dataset]
    args.domain_num = len(tmpp)

    for i, item in enumerate(tmpp):
        tdata = pcross_act.ActList(
            args,
            args.dataset,
            args.data_dir,
            item,
            i,
            transform=actutil.act_train(),
            use_gnn=args.use_gnn  # 👈 Pass GNN flag to dataset
        )
        if i in args.test_envs:
            target_datalist.append(tdata)
        else:
            source_datasetlist.append(tdata)

            steps = len(tdata) / args.batch_size
            if steps < args.steps_per_epoch:
                args.steps_per_epoch = steps

    val_rate = 0.2
    args.steps_per_epoch = int(args.steps_per_epoch * (1 - val_rate))

    # Combine source datasets - convert .x from tensor to numpy before concatenation
    x_list, c_list, p_list, s_list = [], [], [], []
    for ds in source_datasetlist:
        x_list.append(ds.x.cpu().numpy() if torch.is_tensor(ds.x) else ds.x)
        c_list.append(ds.c)
        p_list.append(ds.p)
        s_list.append(ds.s)

    x = np.concatenate(x_list)
    c = np.concatenate(c_list)
    p = np.concatenate(p_list)
    s = np.concatenate(s_list)

    combined_source_dataset = combindataset(args, x, c, p, s)

    total_len = len(combined_source_dataset)
    indices = np.arange(total_len)
    np.random.seed(args.seed)
    np.random.shuffle(indices)

    val_size = int(total_len * val_rate)
    train_indices, val_indices = indices[val_size:], indices[:val_size]

    train_subset = subdataset(args, combined_source_dataset, train_indices)
    val_subset = subdataset(args, combined_source_dataset, val_indices)

    # Combine target datasets similarly
    x_list, c_list, p_list, s_list = [], [], [], []
    for ds in target_datalist:
        x_list.append(ds.x.cpu().numpy() if torch.is_tensor(ds.x) else ds.x)
        c_list.append(ds.c)
        p_list.append(ds.p)
        s_list.append(ds.s)

    x = np.concatenate(x_list)
    c = np.concatenate(c_list)
    p = np.concatenate(p_list)
    s = np.concatenate(s_list)

    combined_target_dataset = combindataset(args, x, c, p, s)

    train_loader, train_loader_noshuffle, valid_loader, target_loader = get_dataloader(
        args, train_subset, val_subset, combined_target_dataset
    )

    return train_loader, train_loader_noshuffle, valid_loader, target_loader, train_subset, val_subset, combined_target_dataset
