from skimage import io, color, transform
import numpy as np
import numpy.ma as ma
import scipy.spatial.distance as distance
from numpy import pi
from math import cos,sqrt
from skimage.segmentation import felzenszwalb
from skimage.util import img_as_float
from glob import glob
from functools import partial
import json, time, random
from PIL import Image, ImageEnhance

def enhance(img):
    res = ImageEnhance.Sharpness(img).enhance(5)
    return res

norm_cache = {}
def norms(mat):
    try:
        return norm_cache[id(mat)]
    except KeyError:
        res = np.apply_along_axis(distance.norm, axis=1, arr=mat)
        norm_cache[id(mat)] = res
        return res

def tile_image(tile, target_size):
    res = Image.new('RGB', target_size)
    target_width, target_height = target_size
    tile_width, tile_height = tile.size
    for left in range(0, target_width, tile_width):
        for top in range(0, target_height, tile_height):
            res.paste(tile, box=(left, top))
    return res

def load_image(fname):
    return Image.open(fname).convert('RGB')

class Segmentation(object):

    def __init__(self, fname):
        self.fname = fname

        print 'loading image'
        img = Image.open(fname)
        img.thumbnail((1280,1024), Image.ANTIALIAS)
        width, height = img.size
        square_size = width * height
        min_size = square_size / 300
        self.raw_img = np.array(enhance(img).convert('RGB'))
        self._segment_ids = None
        img_float = img_as_float(self.raw_img)
        print 'segmenting image'
        self.segments = felzenszwalb(img_float, scale=300, sigma=0.25, min_size=min_size)

    def load_image(self, fname, shape):
        return np.array(tile_image(load_image(fname), (shape[1], shape[0])))
        #return np.array(load_image(fname).resize((shape[1], shape[0])))

    def segment_mask(self, segment_id):
        mask = np.empty(self.segments.shape)
        mask.fill(segment_id)
        return np.equal(self.segments, mask)

    def segment_ids(self):
        if not self._segment_ids:
            self._segment_ids = np.unique(self.segments)
        return self._segment_ids

    def __iter__(self):
        for id in self.segment_ids():
            yield self.segment_img_data(id)

    def apply_textures(self, vectors, fnames):
        ids = self.segment_ids()
        count = ids.shape[0]
        done = 0
        picked_textures = np.ones(vectors.shape[0])
        for segment_id in ids:
            print float(done) / count * 100
            done += 1
            mask = self.segment_mask(segment_id)
            vector = feature_vector(self.raw_img[np.nonzero(mask)])

            # compute cosine similarity
            dots = np.einsum('ij,ij->i', vectors, np.resize(vector, vectors.shape))
            v_norm = np.resize(distance.norm(vector), vectors.shape[0])
            m_norm = norms(vectors)
            scales = v_norm * m_norm
            cosine_similarities = dots / scales

            similarities = cosine_similarities / picked_textures

            idx = np.argmax(similarities)
            picked_textures[idx] += (picked_textures[idx] * 10)
            #picked_textures[idx] += 1

            fname = fnames[idx]
            texture = self.load_image(fname, self.raw_img.shape)
            self.raw_img[mask] = texture[mask]

    def save(self, fname):
        io.imsave(fname, self.raw_img)

    def to_pil(self):
        return Image.fromarray(self.raw_img)

def feature_vector(image):
    hist, edges = np.histogram(image, bins=256)
    #total = np.sum(hist)
    return hist

def vectors_from_images(fnames):
    vectors = []
    for fname in fnames:
        print fname
        img = load_image(fname)
        vec = feature_vector(img)
        vectors.append(vec)
    return np.array(vectors)

def save_vectors(folder, fnames, vectors):
    with open('%s/fnames.json' % folder, 'w') as f:
        json.dump(fnames, f)
    np.save('%s/vectors.npy' % folder, vectors)

def load_vectors(folder):
    with open('%s/fnames.json' % folder, 'r') as f:
        fnames = json.load(f)
    vecs = np.load('%s/vectors.npy' % folder)
    return (fnames, vecs)

def build_dataset(dataset_dir, metadata_dir, sample_size):
    names = glob('%s/*.jpeg' % dataset_dir)
    names = random.sample(names, sample_size)
    vectors = vectors_from_images(names)
    save_vectors(metadata_dir, names, vectors)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print 'invalid arguments'
        sys.exit(2)
    sample_size, target_dir = sys.argv[1:]
    build_dataset('images', target_dir, int(sample_size))
    print 'loading corpus'
    fnames, vectors = load_vectors(target_dir)
    pattern = '/'.join((target_dir, '*'))
    skippable = ['_processed.png', '.json', '.npy']
    for target in glob(pattern):
        if len(list(filter(lambda ext: target.endswith(ext), skippable))) > 0:
            continue
        try:
            print target
            seg = Segmentation(target)
            print 'applying textures'
            seg.apply_textures(vectors, fnames)
            seg.save('%s_processed.png' % target.split('.')[0])
        except (ValueError, MemoryError):
            continue
