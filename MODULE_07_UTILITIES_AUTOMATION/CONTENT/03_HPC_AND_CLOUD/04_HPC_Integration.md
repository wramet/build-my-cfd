# HPC Integration

การเชื่อมต่อกับระบบ HPC

---

## 📋 Learning Objectives

After completing this section, you will be able to:
- ✅ Understand HPC architectures and job schedulers for OpenFOAM
- ✅ Configure SLURM, PBS, and SGE job scripts effectively
- ✅ Optimize data transfer between local systems and HPC clusters
- ✅ Set up and run OpenFOAM on major cloud platforms (AWS, Azure, GCP)
- ✅ Implement cost optimization strategies for cloud-based CFD
- ✅ Apply security best practices for HPC environments
- ✅ Troubleshoot common HPC-specific issues

**⏱️ Estimated Completion Time:** 45 minutes  
**📊 Difficulty Level:** Intermediate  
**🎯 Prerequisites:** Completion of [01_Domain_Decomposition.md](01_Domain_Decomposition.md) and [02_Performance_Monitoring.md](02_Performance_Monitoring.md)

---

## 📚 Prerequisites

Before proceeding, ensure you have:
- ✅ Basic Linux command line proficiency
- ✅ Understanding of domain decomposition principles
- ✅ Access to an HPC cluster or cloud platform account
- ✅ Completed local OpenFOAM simulations successfully
- ✅ SSH key authentication configured (for remote access)

---

## 🎯 Overview

> **What:** Run OpenFOAM simulations on **High-Performance Computing (HPC) clusters and cloud platforms** to leverage massive parallel processing power
>
> **Why:** HPC resources enable you to:
> - Solve **larger problems** (millions of cells) that exceed local workstation capabilities
> - Reduce **simulation time** from days to hours through parallel processing
> - Access **specialized hardware** (high-memory nodes, GPUs) for specific physics
> - Scale **parametric studies** across multiple jobs simultaneously
> - Improve **resource utilization** with dedicated compute infrastructure
>
> **How:** This module covers job scheduler configuration, workflow optimization, cloud platform setup, cost management, security practices, and troubleshooting for production HPC environments

---

## 1. Understanding HPC Architectures

### 1.1 What is HPC?

**HPC (High-Performance Computing)** aggregates computing power to solve complex problems that are too large for standard computers. In CFD context:

```
Workstation          →  HPC Cluster                →  Supercomputer
├─ 1-32 cores        →  ├─ 100-10,000+ cores       →  ├─ 100,000+ cores
├─ 16-128 GB RAM     →  ├─ 256 GB - 4 TB RAM       →  ├─ 10+ TB RAM
├─ Days/weeks        →  ├─ Hours/days              →  ├─ Minutes/hours
└─ Single user       →  └─ Multiple users          →  └─ Thousands of users
```

### 1.2 Key Components

| Component | Purpose | OpenFOAM Relevance |
|-----------|---------|-------------------|
| **Login Node** | Job submission, compilation | Edit cases, submit jobs |
| **Compute Node** | Actual computation | Run solvers, post-processing |
| **Storage** | Shared file system | Store cases, results |
| **Scheduler** | Resource allocation | Manage job queues |
| **Interconnect** | Node communication | MPI performance critical |

### 1.3 Job Schedulers

| Scheduler | Common On | Command Syntax | Market Share |
|-----------|-----------|----------------|--------------|
| **SLURM** | Most modern clusters | `#SBATCH` | ~60% |
| **PBS** | Academic, gov't | `#PBS` | ~25% |
| **SGE/OGE** | Older systems | `#$` | ~10% |
| **LSF** | Corporate, IBM | `#BSUB` | ~5% |

---

## 2. SLURM Configuration (Primary Focus)

### 2.1 Basic Job Script

```bash
#!/bin/bash
#SBATCH --job-name=OpenFOAM_Case           # Job name
#SBATCH --output=results.%j.out            # Output file (%j=jobID)
#SBATCH --error=results.%j.err             # Error file
#SBATCH --nodes=2                          # Number of nodes
#SBATCH --ntasks=64                        # Total MPI ranks
#SBATCH --ntasks-per-node=32               # Ranks per node
#SBATCH --cpus-per-task=1                  # OpenMP threads per rank
#SBATCH --time=24:00:00                    # Walltime (HH:MM:SS)
#SBATCH --mem=0                            # All memory per node
#SBATCH --partition=standard               # Queue/partition name
#SBATCH --mail-type=ALL                    # Email notifications
#SBATCH --mail-user=user@example.com       # Email address

# --- Environment Setup ---
module purge
module load openfoam/10
module load mpi/openmpi

# --- Job Execution ---
echo "Job started on1$(hostname) at1$(date)"
echo "Working directory:1$PWD"
echo "Job ID:1$SLURM_JOB_ID"

# Load OpenFOAM environment
source1$WM_PROJECT_DIR/etc/bashrc

# Run OpenFOAM case
cd1$SLURM_SUBMIT_DIR

# Decompose (if needed)
if [ ! -d "processor0" ]; then
    echo "Decomposing case..."
    decomposePar
fi

# Run solver
echo "Running solver..."
mpirun -np1$SLURM_NTASKS simpleFoam -parallel

# Reconstruct
echo "Reconstructing case..."
reconstructPar

# Post-process
echo "Running paraFoam..."
paraFoam -batch

echo "Job completed at1$(date)"
```

### 2.2 Advanced SLURM Options

```bash
#!/bin/bash
#SBATCH --exclusive                      # Entire node allocation
#SBATCH --oversubscribe                  # Allow node sharing (caution!)
#SBATCH --constraint=cascadelake         # Specific CPU architecture
#SBATCH --gres=gpu:4                     # Request 4 GPUs
#SBATCH --qos=debug                      # Quality of Service (short queue)
#SBATCH --requeue                        # Auto-requeue on node failure
#SBATCH --account=project123             # Project allocation charging

# --- GPU Configuration ---
#SBATCH --gres=gpu:4                     # 4 GPUs per node
#SBATCH --gpu-bind=closest               # Bind MPI ranks to GPUs

# --- Hybrid MPI+OpenMP ---
#SBATCH --ntasks=16                      # 16 MPI ranks
#SBATCH --cpus-per-task=4                # 4 OpenMP threads per rank
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PLACES=cores
export OMP_PROC_BIND=close

# --- Memory Optimization ---
#SBATCH --mem-per-cpu=4000               # 4GB per CPU core
# OR
#SBATCH --mem=250G                       # 250GB total per node
```

### 2.3 Job Dependencies

```bash
# Submit multiple dependent jobs
JOB1=$(sbatch --parsable mesh.sh)        # Generate mesh
JOB2=$(sbatch --parsable --dependency=afterok:$JOB1 decompose.sh)
JOB3=$(sbatch --parsable --dependency=afterok:$JOB2 solve.sh)
JOB4=$(sbatch --parsable --dependency=afterok:$JOB3 postprocess.sh)

echo "Submitted workflow:1$JOB1 →1$JOB2 →1$JOB3 →1$JOB4"
```

---

## 3. PBS Configuration

### 3.1 Basic PBS Script

```bash
#!/bin/bash
#PBS -N OpenFOAM_Case                  # Job name
#PBS -o results.$PBS_JOBID.out         # Output file
#PBS -e results.$PBS_JOBID.err         # Error file
#PBS -l select=2:ncpus=32:mpiprocs=32  # 2 nodes, 32 CPUs each
#PBS -l walltime=24:00:00              # Walltime
#PBS -q standard                       # Queue name
#PBS -M user@example.com               # Email
#PBS -m abe                            # Mail on (a)bort, (b)egin, (e)nd
#PBS -j oe                             # Join output and error

# --- Environment Setup ---
module purge
module load openfoam/10
module load mpi/openmpi

# --- Job Execution ---
cd1$PBS_O_WORKDIR

echo "Job started on1$(hostname) at1$(date)"
echo "Job ID:1$PBS_JOB_ID"
echo "Number of nodes:1$PBS_NUM_NODES"

source1$WM_PROJECT_DIR/etc/bashrc

# Decompose
if [ ! -d "processor0" ]; then
    decomposePar
fi

# Run solver
mpirun -np1$PBS_NP simpleFoam -parallel

# Reconstruct
reconstructPar

echo "Job completed at1$(date)"
```

### 3.2 Advanced PBS Options

```bash
#PBS -l select=2:ncpus=32:mpiprocs=32:mem=250G  # Memory per node
#PBS -l place=pack:group=1                        # Pack nodes together
#PBS -l qos=debug                                 # Quality of Service
#PBS -W group_list=project123                     # Project allocation
#PBS -l select=1:ncpus=48:mpiprocs=16+1:ncpus=48:mpiprocs=32  # Heterogeneous allocation
```

---

## 4. SGE/OGE Configuration

```bash
#!/bin/bash
#1-N OpenFOAM_Case                    # Job name
#1-cwd                                # Change to working directory
#1-j y                                # Join output/error
#1-o output.$JOB_ID.txt               # Output file
#1-pe mpi 64                          # Parallel environment, 64 slots
#1-l h_rt=24:00:00                    # Runtime limit
#1-l h_vmem=4G                        # Memory per slot
#1-M user@example.com                 # Email
#1-m be                               # Email on begin/end

# --- Environment Setup ---
module purge
module load openfoam/10
module load mpi/openmpi

# --- Job Execution ---
echo "Job started on1$(hostname) at1$(date)"
echo "Job ID:1$JOB_ID"
echo "NSLOTS:1$NSLOTS"

source1$WM_PROJECT_DIR/etc/bashrc

# Decompose
if [ ! -d "processor0" ]; then
    decomposePar
fi

# Run solver
mpirun -np1$NSLOTS simpleFoam -parallel

# Reconstruct
reconstructPar

echo "Job completed at1$(date)"
```

---

## 5. Cloud Platform Integration

### 5.1 AWS (Amazon Web Services)

#### 5.1.1 Setup Overview

```bash
# 1. Install AWS CLI
pip install awscli

# 2. Configure credentials
aws configure

# 3. Launch HPC instance
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \      # OpenFOAM AMI
  --instance-type c5n.18xlarge \           # 72 cores, 192 GB RAM
  --count 2 \                              # 2 instances
  --key-name my-key-pair \
  --security-group-ids sg-12345678 \
  --subnet-id subnet-12345678 \
  --iam-instance-profile Name=HPCRole \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=OpenFOAM}]'
```

#### 5.1.2 Recommended Instance Types

| Instance Type | Cores | RAM | Use Case | Cost/hr (approx) |
|--------------|-------|-----|----------|-----------------|
| **c5n.18xlarge** | 72 | 192 GB | Standard CFD |1$2.50 |
| **c5.24xlarge** | 96 | 192 GB | High core count |1$3.60 |
| **z1d.12xlarge** | 48 | 384 GB | Large mesh cases |1$2.40 |
| **p3.8xlarge** | 32 | 248 GB | GPU acceleration |1$6.50 |
| **hpc6a.48xlarge** | 192 | 384 GB | HPC-optimized |1$4.00 |

#### 5.1.3 AWS ParallelCluster

```bash
# Install AWS ParallelCluster
pip install aws-parallelcluster

# Initialize configuration
pcluster configure

# config.yaml example
Region: us-east-1
Image:
  Os: alinux2
HeadNode:
  InstanceType: t2.large
  Networking:
    SubnetId: subnet-12345678
  Ssh:
    KeyName: my-key-pair
Scheduling:
  Scheduler: slurm
  SlurmQueues:
    - Name: spot
      ComputeResources:
        - Name: compute
          InstanceType: c5n.18xlarge
          MinCount: 0
          MaxCount: 20
          SpotPrice: 0.5
      Networking:
        SubnetIds:
          - subnet-12345678

# Create cluster
pcluster create my-hpc-cluster

# SSH to head node
pcluster ssh my-hpc-cluster

# Submit job
sbatch run.slurm
```

#### 5.1.4 AWS FSx for Lustre (High-Performance Storage)

```bash
# Create FSx for Lustre filesystem
aws fsx create-file-system \
  --file-system-type LUSTRE \
  --storage-capacity 1200 \
  --subnet-id subnet-12345678 \
  --security-group-ids sg-12345678 \
  --lustre-configuration AutoImportPolicy=NEW_CHANGED,AutoExportPolicy=NEW_CHANGED

# Mount on compute nodes
sudo mount -t lustre fs-12345678.fsx.us-east-1.amazonaws.com@tcp:/fsx /fsx

# Use for case files
cp -r case/ /fsx/
cd /fsx/case
mpirun simpleFoam -parallel
```

---

### 5.2 Azure (Microsoft Azure)

#### 5.2.1 Azure CycleCloud Setup

```bash
# 1. Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# 2. Login
az login

# 3. Create CycleCloud cluster
az cyclecloud create-cluster \
  --name openfoam-cluster \
  --resource-group OpenFOAM-RG \
  --location eastus \
  --scheduler slurm \
  --vm-size Standard_HB120rs_v2 \
  --max-node-count 20

# 4. SSH to head node
az cyclecloud ssh-cluster \
  --name openfoam-cluster \
  --resource-group OpenFOAM-RG \
  --user azureuser

# 5. Submit job
sbatch run.slurm
```

#### 5.2.2 Recommended VM Sizes

| VM Size | Cores | RAM | Network | Use Case |
|---------|-------|-----|---------|----------|
| **HB120rs_v2** | 120 | 480 GB | 200 Gbps | Large parallel CFD |
| **HC44rs** | 44 | 352 GB | 100 Gbps | MPI-heavy workloads |
| **HB60rs** | 60 | 240 GB | 100 Gbps | Memory-intensive |
| **ND96asr_v4** | 96 | 900 GB | - | GPU-accelerated |

#### 5.2.3 Azure Batch Setup

```python
# azure_batch_setup.py
from azure.batch import BatchServiceClient
from azure.batch.batch_auth import SharedKeyCredentials
import azure.batch.models as batchmodels

# Configure
credentials = SharedKeyCredentials(account_name, account_key)
batch_client = BatchServiceClient(credentials, batch_url)

# Create pool
pool = batchmodels.PoolAddParameter(
    id="openfoam-pool",
    vm_size="STANDARD_HC44RS",
    virtual_machine_configuration=batchmodels.VirtualMachineConfiguration(
        image_reference=batchmodels.ImageReference(
            publisher="canonical",
            offer="ubuntuserver",
            sku="18.04-lts",
            version="latest"
        ),
        node_agent_sku_id="batch.node.ubuntu 18.04"
    ),
    target_dedicated_nodes=10,
    enable_inter_node_communication=True,
    task_slots_per_node=44
)

batch_client.pool.add(pool)

# Create job
job = batchmodels.JobAddParameter(
    id="openfoam-job",
    pool_info=batchmodels.PoolInformation(pool_id="openfoam-pool")
)

batch_client.job.add(job)

# Create task
task = batchmodels.TaskAddParameter(
    id="cfd-task",
    command_line="mpirun -np 440 simpleFoam -parallel"
)

batch_client.task.add(job_id="openfoam-job", task_id="cfd-task", task=task)
```

#### 5.2.4 Azure Files & NetApp Files

```bash
# Create Azure NetApp Files
az netappfiles volume create \
  --resource-group OpenFOAM-RG \
  --account-name anf-account \
  --pool-name anf-pool \
  --name openfoam-vol \
  --location eastus \
  --service-level Premium \
  --usage-threshold 1073741824 \
  --creation-token anf-volume \
  --subnet-id /subscriptions/.../resourceGroups/.../providers/Microsoft.Network/virtualNetworks/.../subnets/...

# Mount on compute nodes
sudo mkdir /mnt/anf
sudo mount -t nfs -o rw,hard,rsize=65536,wsize=65536,tcp 10.0.0.4:/anf-volume /mnt/anf
```

---

### 5.3 GCP (Google Cloud Platform)

#### 5.3.1 Google Cloud Setup

```bash
# 1. Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l1$SHELL
gcloud init

# 2. Create Compute Engine instance
gcloud compute instances create openfoam-node \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --machine-type=n2-highmem-96 \
  --min-cpu-platform="Intel Cascade Lake" \
  --zone=us-central1-a \
  --boot-disk-size=200GB \
  --boot-disk-type=pd-ssd

# 3. Install OpenFOAM
gcloud compute ssh openfoam-node --zone=us-central1-a
sudo apt-get update
sudo apt-get install openfoam10

# 4. Run simulation
mpirun -np 96 simpleFoam -parallel
```

#### 5.3.2 Recommended Machine Types

| Machine Type | Cores | RAM | Use Case | Cost/hr |
|--------------|-------|-----|----------|---------|
| **n2-highmem-96** | 96 | 768 GB | Large cases |1$6.00 |
| **n2-highcpu-128** | 128 | 512 GB | CPU-intensive |1$5.00 |
| **c2-standard-112** | 112 | 448 GB | Compute-optimized |1$4.50 |
| **n2d-highmem-96** | 96 | 768 GB | AMD-based |1$4.00 |
| **a2-highgpu-8g** | 96 | 860 GB | GPU (8x A100) |1$12.00 |

#### 5.3.3 Cloud HPC Toolkit

```bash
# Install Slurm on GCP
git clone https://github.com/GoogleCloudPlatform/slurm-gcp
cd slurm-gcp

# Configure deployment
cp config.yaml.example config.yaml
# Edit config.yaml with project settings

# Deploy cluster
./deploy.sh create

# Access head node
gcloud compute ssh slurm-controller --zone=us-central1-a

# Submit job
sbatch run.slurm
```

#### 5.3.4 Filestore Setup

```bash
# Create Filestore instance
gcloud filestore instances create openfoam-fs \
  --zone=us-central1-c \
  --tier=PREMIUM \
  --file-share=name="nfsvol",capacity=1TB \
  --network=name="default",reserved-ip-range="10.0.0.0/29"

# Mount on compute nodes
sudo mount -t nfs 10.0.0.2:/nfsvol /mnt/filestore

# Use for case files
cp -r case/ /mnt/filestore/
cd /mnt/filestore/case
mpirun simpleFoam -parallel
```

---

## 6. Data Transfer Optimization

### 6.1 Transfer Protocols Comparison

| Tool | Speed | Compression | Resume | Best For |
|------|-------|-------------|--------|----------|
| **rsync** | Medium | Yes | Yes | Incremental sync |
| **scp** | Slow | No | No | Small files |
| **bbcp** | Fast | No | No | Large single files |
| **globus** | Fast | Yes | Yes | Very large datasets |
| **aspera** | Very Fast | Yes | Yes | Enterprise transfer |

### 6.2 Optimized rsync Commands

```bash
# Basic rsync
rsync -avz case/ cluster:~/cases/

# Optimized for bandwidth
rsync -avz --progress --partial \
  case/ cluster:~/cases/

# Parallel rsync (multiple files)
rsync -avz --progress --partial \
  --numcopies=4 \
  case/ cluster:~/cases/

# Compress during transfer
rsync -avzz --progress \
  case/ cluster:~/cases/

# Exclude unnecessary files
rsync -avz --exclude='processor*' \
  --exclude='*.bak' \
  --exclude='0.*' \
  case/ cluster:~/cases/

# Transfer only processor directories
rsync -avz --include='processor*/' \
  --include='processor*/**' \
  --exclude='*' \
  case/ cluster:~/cases/
```

### 6.3 Archive Before Transfer

```bash
# Create tar archive
tar czf case.tar.gz case/

# Transfer archive
rsync -avz --progress case.tar.gz cluster:~/

# Extract on cluster
ssh cluster "tar xzf case.tar.gz"
```

### 6.4 Globus Transfer (Recommended for Large Datasets)

```bash
# 1. Install Globus CLI
pip install globus-cli

# 2. Authenticate
globus login

# 3. Transfer files
globus transfer \
  --source-endpoint1$SOURCE_UUID \
  --dest-endpoint1$DEST_UUID \
  /path/to/source \
  /path/to/dest

# 4. Monitor transfer
globus task wait1$TASK_ID
```

---

## 7. Interactive vs Batch Jobs

### 7.1 Comparison

| Aspect | Interactive | Batch |
|--------|-------------|-------|
| **Use Case** | Development, debugging | Production runs |
| **Job Duration** | Short (< 2 hours) | Long (hours to days) |
| **Resource Allocation** | Immediate | Queued |
| **Cost (Cloud)** | Higher (on-demand) | Lower (spot/preemptible) |
| **Scalability** | Limited | Unlimited |
| **Automation** | Manual | Fully automated |

### 7.2 Interactive Job Examples

```bash
# SLURM Interactive
salloc --nodes=1 --ntasks=32 --time=2:00:00 --pty bash

# PBS Interactive
qsub -I -l select=1:ncpus=32 -l walltime=2:00:00

# SGE Interactive
qsh -pe mpi 32 -l h_rt=2:00:00

# Once in interactive session:
cd case/
decomposePar
mpirun -np 32 simpleFoam -parallel
# Monitor output in real-time
```

### 7.3 Batch Job Workflow

```bash
# 1. Create job script
cat > run.slurm << 'EOF'
#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks=128
#SBATCH --time=48:00:00
#SBATCH --partition=standard

module load openfoam
cd1$SLURM_SUBMIT_DIR
decomposePar
mpirun -np1$SLURM_NTASKS simpleFoam -parallel
reconstructPar
EOF

# 2. Submit job
sbatch run.slurm

# 3. Monitor job
watch -n 5 squeue -u1$USER

# 4. Check output
tail -f slurm-12345.out
```

---

## 8. Cost Optimization for Cloud

### 8.1 Spot/Preemptible Instances

| Platform | Spot Name | Savings | Disruption |
|----------|-----------|---------|------------|
| **AWS** | Spot Instances | 70-90% | 2-minute warning |
| **Azure** | Low-priority VMs | 60-80% | 30-second warning |
| **GCP** | Preemptible VMs | 60-80% | 30-second warning |

```bash
# AWS Spot Instance
aws ec2 run-instances \
  --instance-market-options "MarketType=spot,SpotOptions={SpotInstanceType=one-time,InstanceInterruptionBehavior=terminate}" \
  --instance-type c5n.18xlarge \
  ...

# Azure Low-priority VM
az batch pool create \
  --target-dedicated 0 \
  --target-low-priority 20 \
  --vm-size Standard_HC44RS \
  ...

# GCP Preemptible VM
gcloud compute instances create openfoam-spot \
  --preemptible \
  --machine-type n2-highmem-96 \
  ...
```

### 8.2 Checkpointing Strategies

```bash
#!/bin/bash
# checkpoint.slurm - Checkpoint every 2 hours

#SBATCH --time=48:00:00
#SBATCH --signal=B:USR1@120  # USR1 signal 120 seconds before time limit

# Trap signal for checkpointing
trap 'echo "Checkpointing..."; foamListTimes -latestTime; exit 0' USR1

# Main solver loop
while true; do
    # Get latest time
    LATEST_TIME=$(foamListTimes -latestTime)
    
    # Run solver for 2 hours
    timeout 7200 simpleFoam -parallel
    
    # Check if job is being preempted
    if [1$? -eq 124 ]; then
        echo "Checkpoint reached at time1$LATEST_TIME"
        break
    fi
done
```

### 8.3 Auto-scaling Strategies

```python
# auto_scale.py - Auto-scale based on queue depth
import boto3
import subprocess

client = boto3.client('ec2')

def get_queue_depth():
    """Get number of pending SLURM jobs"""
    result = subprocess.run(['squeue', '-h', '-p', 'standard', '-t', 'pending'],
                          capture_output=True, text=True)
    return len(result.stdout.splitlines())

def scale_cluster():
    """Scale cluster based on queue depth"""
    queue_depth = get_queue_depth()
    desired_nodes = max(1, queue_depth // 32)  # 32 tasks per node
    
    # Update cluster size
    response = client.modify_instance_attribute(
        InstanceId='i-1234567890abcdef0',
        InstanceType={'Value': f'c5n.18xlarge'}
    )
    
    print(f"Scaled to {desired_nodes} nodes")

if __name__ == '__main__':
    scale_cluster()
```

### 8.4 Reserved Instances

| Platform | Reservation Type | Savings | Commitment |
|----------|------------------|---------|------------|
| **AWS** | Reserved Instances | 40-60% | 1-3 years |
| **Azure** | Reserved VM Instances | 40-60% | 1-3 years |
| **GCP** | Committed Use Discounts | 40-60% | 1-3 years |

---

## 9. Security Best Practices

### 9.1 SSH Key Management

```bash
# 1. Generate SSH key pair
ssh-keygen -t ed25519 -C "user@cluster" -f ~/.ssh/cluster_key

# 2. Copy public key to cluster
ssh-copy-id -i ~/.ssh/cluster_key.pub user@cluster

# 3. Use ssh config
cat > ~/.ssh/config << 'EOF'
Host cluster
    HostName cluster.example.com
    User username
    IdentityFile ~/.ssh/cluster_key
    ForwardX11 no
    ForwardAgent yes
EOF

# 4. Test connection
ssh cluster
```

### 9.2 Firewall Configuration

```bash
# AWS Security Group Rules
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.0/24  # Your IP range only

# Azure Network Security Group
az network nsg rule create \
  --nsg-name cluster-nsg \
  --name allow-ssh \
  --priority 1000 \
  --access Allow \
  --protocol Tcp \
  --direction Inbound \
  --source-address-prefixes 203.0.113.0/24 \
  --destination-port-ranges 22

# GCP Firewall Rule
gcloud compute firewall-rules create allow-ssh \
  --allow tcp:22 \
  --source-ranges 203.0.113.0/24 \
  --network default
```

### 9.3 Data Encryption

```bash
# Encrypt data before transfer
openssl enc -aes-256-cbc -salt -in case.tar.gz -out case.tar.gz.enc

# Transfer encrypted file
rsync -avz case.tar.gz.enc cluster:~/

# Decrypt on cluster
ssh cluster "openssl enc -d -aes-256-cbc -in case.tar.gz.enc -out case.tar.gz"
```

### 9.4 Access Control

```bash
# Set appropriate file permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

# Group permissions for shared projects
chmod -R 770 /shared/project/
chgrp -R project-group /shared/project/

# Set umask for new files
echo "umask 027" >> ~/.bashrc
```

---

## 10. Troubleshooting HPC Issues

### 10.1 Common Issues and Solutions

#### Issue 1: Job Won't Start

**Symptoms:**
```
sbatch: Submitted batch job 12345
squeue: Job 12345 is in PENDING state indefinitely
```

**Solutions:**
```bash
# Check queue status
squeue -u1$USER -o "%.18i %.9P %.20j %.8u %.2t %.10M %.6D %R"

# Check why job is pending
scontrol show job 12345

# Common reasons:
# 1. Insufficient resources
sinfo -o "%P %a %l %D %N"

# 2. Time limit exceeds queue maximum
sacctmgr show qos format=Name,MaxWall

# 3. Fair-share throttling
sshare -a
```

#### Issue 2: MPI Communication Errors

**Symptoms:**
```
Fatal error in MPI_Point_to_point: Invalid rank, error stack:
MPI_Comm_rank: Invalid communicator
```

**Solutions:**
```bash
# Check number of processors matches decomposition
ls -d processor* | wc -l
echo1$SLURM_NTASKS

# Ensure correct number of MPI ranks
mpirun -np1$(ls -d processor* | wc -l) simpleFoam -parallel

# Check for host file issues
cat1$SLURM_JOB_NODELIST
```

#### Issue 3: Out of Memory Errors

**Symptoms:**
```
simpleFoam: error: allocation failed
```

**Solutions:**
```bash
# Check memory usage
free -h
sacct -j 12345 --format=JobID,JobName,MaxRSS

# Request more memory
#SBATCH --mem-per-cpu=8000  # 8GB per CPU

# Use decomposeParDict to reduce per-processor memory
# in system/decomposeParDict
numberOfSubdomains 64;
method simple;
simpleCoeffs
{
    n (4 4 4);  // Adjust distribution
}
```

#### Issue 4: I/O Bottlenecks

**Symptoms:**
```
Solver spends excessive time writing results
```

**Solutions:**
```bash
# 1. Reduce write frequency
// in system/controlDict
writeControl    timeStep;
writeInterval   500;  // Increase from default

# 2. Use compressed output
// in system/controlDict
writeCompression on;

# 3. Write to fast local storage, then move to shared storage
#SBATCH --tmp=500  # Request 500GB local storage

# 4. Disable unnecessary output
// in system/controlDict
functions
{
    // Comment out unused functions
}
```

#### Issue 5: Slow Interconnect Performance

**Symptoms:**
```
MPI communication dominates runtime
```

**Solutions:**
```bash
# Test interconnect performance
mpirun -np1$SLURM_NTASKS osu_latency

# Check if using expected interconnect
ibstat  # InfiniBand
ibdevsnetdev

# Bind MPI processes to cores
mpirun --bind-to core --map-by socket:PE=1 \
  -np1$SLURM_NTASKS simpleFoam -parallel

# Use optimized MPI flags
export I_MPI_FABRICS=ofi
export I_MPI_PROVIDER=psm2
```

### 10.2 Debugging Workflow

```bash
#!/bin/bash
# debug_workflow.sh

# 1. Test on single processor
echo "Testing single processor..."
simpleFoam > serial.log 2>&1

# 2. Test small parallel run
echo "Testing 4 processors..."
decomposePar -cellDist
mpirun -np 4 simpleFoam -parallel > parallel.log 2>&1

# 3. Check for errors
if grep -i "error\|fatal\|failed" serial.log; then
    echo "Errors in serial run"
    exit 1
fi

if grep -i "error\|fatal\|failed" parallel.log; then
    echo "Errors in parallel run"
    exit 1
fi

# 4. Compare results
echo "Comparing results..."
foamListTimes
# Compare final time directories
diff -r 0.001_serial 0.001_parallel/processor0
```

---

## 11. Practical Example: Complete HPC Workflow

### 11.1 Local Preparation

```bash
#!/bin/bash
# prepare_local.sh

# 1. Complete simulation locally first
cd case/
blockMesh
checkMesh
snappyHexMesh -overwrite
decomposePar

# 2. Test short run
mpirun -np 4 simpleFoam -parallel

# 3. Clean results (keep mesh)
rm -r processor*/[0-9]*
foamListTimes -rm

# 4. Create archive
tar czf case.tar.gz case/
```

### 11.2 Transfer to HPC

```bash
#!/bin/bash
# transfer_to_hpc.sh

CLUSTER="cluster.example.com"
REMOTE_DIR="~/cases/openfoam"

# 1. Transfer case
rsync -avz --progress \
  --exclude='processor*' \
  case.tar.gz1$CLUSTER:$REMOTE_DIR/

# 2. Transfer decomposition
rsync -avz --progress \
  case/system/decomposeParDict \
1$CLUSTER:$REMOTE_DIR/case/system/
```

### 11.3 Submit HPC Job

```bash
#!/bin/bash
# submit_hpc_job.sh

# 1. Create job script
cat > run.slurm << 'EOF'
#!/bin/bash
#SBATCH --job-name=openfoam_case
#SBATCH --nodes=8
#SBATCH --ntasks=256
#SBATCH --time=72:00:00
#SBATCH --partition=standard
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=user@example.com

module purge
module load openfoam/10
module load mpi/openmpi

cd1$SLURM_SUBMIT_DIR

# Extract case
tar xzf case.tar.gz
cd case/

# Decompose
decomposePar

# Run solver
mpirun -np1$SLURM_NTASKS simpleFoam -parallel

# Reconstruct
reconstructPar -latestTime

# Create VTK files for visualization
foamToVTK -latestTime

EOF

# 2. Submit job
sbatch run.slurm

# 3. Monitor job
watch -n 10 squeue -u1$USER
```

### 11.4 Monitor and Retrieve Results

```bash
#!/bin/bash
# monitor_and_retrieve.sh

CLUSTER="cluster.example.com"
REMOTE_DIR="~/cases/openfoam"
JOB_ID=$1

# 1. Monitor job
while true; do
    STATUS=$(ssh1$CLUSTER "squeue -j1$JOB_ID -o %T | tail -n 1")
    echo "Job status:1$STATUS"
    
    if [ "$STATUS" = "COMPLETED" ]; then
        echo "Job completed successfully"
        break
    fi
    
    sleep 60
done

# 2. Check for errors
ssh1$CLUSTER "cat1$REMOTE_DIR/slurm-$JOB_ID.err" | grep -i error

# 3. Retrieve results
rsync -avz --progress \
1$CLUSTER:$REMOTE_DIR/case/VTK/ \
  ./results/VTK/

# 4. Retrieve log files
scp1$CLUSTER:$REMOTE_DIR/slurm-$JOB_ID.* ./
scp1$CLUSTER:$REMOTE_DIR/case/log.simpleFoam ./
```

---

## 12. Quick Reference

### 12.1 Scheduler Commands

| Action | SLURM | PBS | SGE |
|--------|-------|-----|-----|
| **Submit** | `sbatch script.sh` | `qsub script.sh` | `qsub script.sh` |
| **Check Status** | `squeue -u1$USER` | `qstat -u1$USER` | `qstat -u1$USER` |
| **Delete Job** | `scancel JOBID` | `qdel JOBID` | `qdel JOBID` |
| **Job Info** | `scontrol show job JOBID` | `qstat -f JOBID` | `qstat -j JOBID` |
| **Queue Info** | `sinfo` | `qstat -Q` | `qstat -g c` |
| **Hold Job** | `scontrol hold JOBID` | `qhold JOBID` | `qhold JOBID` |
| **Release Hold** | `scontrol release JOBID` | `qrls JOBID` | `qrls JOBID` |

### 12.2 Environment Modules

```bash
# Available modules
module avail openfoam

# Load specific version
module load openfoam/10

# List loaded modules
module list

# Unload module
module unload openfoam

# Show module information
module show openfoam/10

# Swap modules
module swap openfoam/9 openfoam/10
```

### 12.3 Common MPI Commands

```bash
# Show MPI ranks
mpirun -np 64 hostname

# Test MPI performance
mpirun -np 64 osu_latency

# Show MPI configuration
mpirun --version

# Bind processes to cores
mpirun --bind-to core --map-by socket -np 64 solver
```

---

## 13. Key Takeaways

### ✅ Essential Points

1. **HPC Fundamentals**
   - HPC clusters use job schedulers (SLURM, PBS, SGE) to manage resources
   - Understanding your scheduler's syntax and options is critical
   - Job scripts require environment setup, execution, and cleanup phases

2. **Cloud Platforms**
   - AWS (c5n, z1d instances), Azure (HB, HC series), GCP (n2, c2 series) offer optimized HPC VMs
   - Spot/preemptible instances offer 60-90% cost savings for fault-tolerant workloads
   - High-performance storage (FSx, NetApp Files, Filestore) is essential for I/O-intensive cases

3. **Data Transfer**
   - Use rsync with compression for incremental transfers
   - Globus is recommended for very large datasets (>100GB)
   - Archive before transfer to reduce file count overhead

4. **Cost Optimization**
   - Use spot/preemptible instances when possible
   - Implement checkpointing to handle preemptions gracefully
   - Consider reserved instances for long-term production workloads

5. **Security**
   - Use SSH key authentication (never passwords)
   - Restrict firewall rules to specific IP ranges
   - Encrypt sensitive data before transfer
   - Set appropriate file permissions

6. **Troubleshooting**
   - Always test locally before submitting to HPC
   - Start with small test runs to validate setup
   - Monitor job logs and system resources actively
   - Check for memory, I/O, and interconnect bottlenecks

### 🔗 Connecting Concepts

- **Domain Decomposition** ([01_Domain_Decomposition.md](01_Domain_Decomposition.md)): Must match your HPC job's requested number of MPI ranks
- **Performance Monitoring** ([02_Performance_Monitoring.md](02_Performance_Monitoring.md)): Essential for identifying HPC bottlenecks
- **Solver Optimization** ([03_Optimization_Techniques.md](03_Optimization_Techniques.md)): Critical for maximizing HPC ROI

---

## 📖 Related Reading

### Prerequisites
- **Decomposition:** [01_Domain_Decomposition.md](01_Domain_Decomposition.md)
- **Monitoring:** [02_Performance_Monitoring.md](02_Performance_Monitoring.md)
- **Optimization:** [03_Optimization_Techniques.md](03_Optimization_Techniques.md)

### Further Reading
- **SLURM Documentation:** https://slurm.schedmd.com/documentation.html
- **AWS HPC:** https://aws.amazon.com/hpc/
- **Azure HPC:** https://azure.microsoft.com/en-us/products/hpc
- **GCP HPC:** https://cloud.google.com/architecture/hpc
- **OpenFOAM HPC Guide:** https://www.openfoam.com/documentation/user-guide/running-applications-parallel

---

## 🎯 Self-Assessment

### Concept Checks

<details>
<summary><b>1. What is the primary purpose of a job scheduler in HPC?</b></summary>

**Answer:** A job scheduler manages resource allocation, job queuing, and execution on shared HPC clusters, ensuring efficient utilization of compute resources among multiple users.
</details>

<details>
<summary><b>2. When should you use spot/preemptible instances instead of on-demand?</b></summary>

**Answer:** Use spot instances for fault-tolerant, checkpointed workloads where job completion time is flexible and you want to minimize costs (60-90% savings).
</details>

<details>
<summary><b>3. Why is data transfer optimization important for cloud HPC?</b></summary>

**Answer:** Optimized data transfer reduces ingress/egress costs, accelerates workflow setup, and minimizes time spent waiting for data to move between local and cloud resources.
</details>

<details>
<summary><b>4. What are the security best practices for HPC environments?</b></summary>

**Answer:** Use SSH key authentication, restrict firewall rules to specific IPs, encrypt sensitive data, set appropriate file permissions, and use VPNs for remote access.
</details>

### Practical Exercises

1. **Basic:** Create a SLURM job script that runs simpleFoam on 4 processors for 1 hour
2. **Intermediate:** Set up an AWS ParallelCluster with SLURM and submit a test job
3. **Advanced:** Implement checkpointing for a 48-hour job that can resume from interruptions
4. **Expert:** Create an auto-scaling script that adjusts cluster size based on SLURM queue depth

---

**Last Updated:** 2024-12-31  
**Version:** 2.0  
**Maintainer:** OpenFOAM Documentation Team  
**License:** Creative Commons Attribution-ShareAlike 4.0