'''
Plotting utilities for the ProTex tool. 
'''

import umap.umap_ as umap
import matplotlib.pyplot as plt
import seaborn as sns
import dataset 
import numpy as np
import pandas as pd

colors = sns.color_palette('Paired')
palette = 'Paired'


def plot_umap(data, filename='umap_plot.png'):
    '''
    Apply UMAP dimensionality reduction to embeddings, and plot in
    two-dimensional space. 
    '''
    reducer = umap.UMAP()
    fig, ax = plt.subplots(1)
    ax.set_xlabel('UMAP 1')
    ax.set_ylabel('UMAP 2')
    
    legend = []

    for label, embeddings in data.items():

        legend.append(label)

        # Need to convert from tensor back to NumPy array, I think.
        reduced_embeddings = reducer.fit_transform(embeddings)
        # print(reduced_embeddings.shape, reduced_embeddings_truncated.shape)
        reduced_embeddings = pd.DataFrame(reduced_embeddings, columns=['UMAP 1', 'UMAP 2'])

        sns.scatterplot(reduced_embeddings, ax=ax, x='UMAP 1', y='UMAP 2')
    
    ax.legend(legend)
    plt.savefig(filename)

# TODO: It might be useful to visualize clusters somehow. Maybe show how they are represented in UMAP
# space... Only issue is that there are over 8000 clusters, so this may not be useful or worthwhile. 

# DATASET VISUALIZATION ---------------------------------------------------------------------------

def plot_dataset_length_distributions(sec_data, short_data):
    '''
    Visualize the length distributions of the short and truncated selenoproteins. 

    args:
        - sec_data (pd.DataFrame)
        - short_data (pd.DataFrame)
    '''
    # sec_data = dataset.fasta_to_df('/home/prichter/Documents/protex/data/sec.fasta')
    # short_data = dataset.fasta_to_df('/home/prichter/Documents/protex/data/sec.fasta')

    plot_data = {}

    # Grab the sequence lengths. 
    sec_lengths = sec_data['seq'].apply(len).to_numpy()
    short_lengths = short_data['seq'].apply(len).to_numpy()
    lengths = np.concatenate([sec_lengths, short_lengths])

    plot_data['length'] = lengths
    plot_data['dataset'] = np.array(['sec'] * len(sec_lengths) + ['short'] * len(short_lengths))
    plot_data = pd.DataFrame(plot_data) # Convert to DataFrame. 

    fig, ax = plt.subplots(1)

    # Add some relevant information to the plot. 
    ax.text(700, 1000, f'sec.fasta size: {len(sec_lengths)}\nshort.fasta size: {len(short_lengths)}', size='small', weight='semibold')
    ax.set_title('Length distributions over sequence datasets')

    sns.histplot(data=plot_data, hue='dataset', x='length', legend=True, ax=ax, palette=palette, multiple='dodge', bins=15)

    fig.savefig('dataset_length_distributions.png', format='png')


# NOTE: There are too many clusters to do a scatter plot with error bar
def plot_cluster_information(fasta_data, clstr_data):
    '''
    Visualize the lengths of different proteins sorted into clusters by CD-hit. 

    args:
        - fasta_data (pd.DataFrame): The data extracted from the FASTA file from which the clstr_data was produced. 
        - clstr_data (pd.DataFrame): The clstr data generated by CD-HIT. 
    '''
    # Join the cluster and sequence data according to genome id. 
    data = clstr_data.merge(fasta_data, how='inner', on='id') # Need to combine the two DataFrames according to the ID column, using intersection of keys from both frames.
    data = data.drop_duplicates(subset=['id']) # Make sure there are no duplicates (I was running into some issues with this)

    plot_data = {}

    data['length'] = data['seq'].apply(len) # Get the lengths. 
    # Get the mean sequence length in each cluster. 

    plot_data['mean'] = data.groupby(['cluster'])['length'].mean()
    # Get the standard deviation of lengths across each cluster. 
    plot_data['std'] = data.groupby(['cluster'])['length'].std(ddof=0) # Use population std deviation, with divisor of N instead of (N - 1)
    # Get the size of each cluster
    plot_data['size'] = data.groupby(['cluster']).size()

    plot_data = pd.DataFrame(plot_data)
    # Portion sizes into bins. A little confused by what the q parameter is. 
    plot_data['size_bins'] = pd.qcut(plot_data['size'].copy(), q=10, retbins=False, duplicates='drop')

    # print(len(plot_data[plot_data['size'] == 1]))
    # print(max(plot_data['size']))

    fig, axes = plt.subplots(3, figsize=(10, 15))

    # Add some relevant information to the plot. 
    nclusters = max(data['cluster']) + 1
    # axes[1].text(10000, 1000, f'n=5, c=0.8 \ncluster count: {nclusters}', size='small', weight='semibold')
    
    axes[0].set_title('Mean sequence length by cluster')
    axes[1].set_title('Standard deviation of sequence length by cluster')
    axes[2].set_title('Cluster size distribution')

    sns.histplot(data=plot_data, x='mean', hue='size_bins', ax=axes[0], bins=20, legend=True, multiple='dodge', stat='count', palette=palette)
    sns.histplot(data=plot_data, x='std', hue='size_bins', ax=axes[1], legend=True, log_scale=(False, True), multiple='dodge', stat='count', palette=palette)
    sns.histplot(data=plot_data, x='size', ax=axes[2], bins=50, log_scale=(False, True), palette=palette)

    axes[0].set_ylabel('count')
    axes[1].set_ylabel('log(count)')
    axes[2].set_ylabel('log(count)')

    fig.savefig('cluster_information.png', format='png')



def plot_train_test_composition(train_data, test_data):
    '''
    '''
    train_labels = dataset.generate_labels(train_data)
    test_labels = dataset.generate_labels(test_data)

    # Label is 1 if the sequence is a selenoprotein. 
    train_sec_count = sum(train_labels)
    test_sec_count = sum(test_labels)

    labels = ['sec', 'short']

    fig, axes = plt.subplots(nrows=1, ncols=2)

    axes[0].pie([train_sec_count, len(train_data) - train_sec_count], labels=labels, autopct='%1.1f%%', colors=colors)
    axes[0].set_title('Training set composition')

    axes[1].pie([test_sec_count, len(test_data) - test_sec_count], labels=labels, autopct='%1.1f%%', colors=colors)
    axes[1].set_title('Testing set composition')

    fig.savefig('train_test_composition.png', format='png')
   



if __name__ == '__main__':
    sec_data = dataset.fasta_to_df('/home/prichter/Documents/protex/data/sec.fasta')
    short_data = dataset.fasta_to_df('/home/prichter/Documents/protex/data/short.fasta')

    # Load in the clustering and sequence information. 
    clstr_data = dataset.clstr_to_df('/home/prichter/Documents/protex/data/all.clstr')
    fasta_data = dataset.fasta_to_df('/home/prichter/Documents/protex/data/all.fasta')

    train_data = pd.read_csv('/home/prichter/Documents/protex/data/train.csv')
    test_data = pd.read_csv('/home/prichter/Documents/protex/data/test.csv')

    plot_dataset_length_distributions(sec_data, short_data)
    # plot_cluster_information(fasta_data, clstr_data)
    # plot_train_test_composition(train_data, test_data)
