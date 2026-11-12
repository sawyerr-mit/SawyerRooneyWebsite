# test_examples.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import pickle
import argparse
import numpy as np
from PIL import Image, ImageFilter
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend, good for scripts
import matplotlib.pyplot as plt

# Import the forward_predict function from your neural net file
# neuralNet.py must be in the same folder (or on PYTHONPATH)
from neuralNet import forward_predict  # returns np.argmax(AL, axis=0)
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# load the pkl file which contrains the parameters we trained
def load_params(path='trained_params.pkl'):
    with open(path, 'rb') as f:
        return pickle.load(f)

# opens image path and resizes down to 28 x 28 - the format used by training data
# ideally inputs should be 28x28 to avoid issues with the neural network
# also applies slight blur to mimic MNIST anti-aliasing and shows the image
def preprocess_image(img_path, invert_if_needed=False, show=False, save_preprocessed="preprocessed_test_image.png"):
    img = Image.open(img_path).convert('L')
    # get numpy copy for bbox detection and polarity handling
    arr0 = np.array(img).astype(np.float32)
    if invert_if_needed:
        arr0 = 255.0 - arr0

    # mild threshold to detect foreground pixels
    thresh = 10
    mask = arr0 > thresh
    coords = np.argwhere(mask)

    if coords.size == 0:
        # empty image fallback: just resize and normalize
        img28 = Image.fromarray(arr0).resize((28, 28), Image.Resampling.LANCZOS)
        img28 = img28.filter(ImageFilter.GaussianBlur(radius=0.5))
        arr = np.array(img28).astype(np.float32) / 255.0
    else:
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0) + 1
        cropped = arr0[y0:y1, x0:x1]

        # resize to fit into 20x20 box while preserving aspect ratio
        h, w = cropped.shape
        if h > w:
            new_h = 20
            new_w = max(1, int(round(w * (20.0 / h))))
        else:
            new_w = 20
            new_h = max(1, int(round(h * (20.0 / w))))
        pil_crop = Image.fromarray(cropped).resize((new_w, new_h), Image.Resampling.LANCZOS)

        # paste into 28x28 canvas centered (4px padding typical for MNIST)
        canvas = Image.new('L', (28, 28), color=0)
        left = (28 - new_w) // 2
        top = (28 - new_h) // 2
        canvas.paste(pil_crop, (left, top))
        arr = np.array(canvas).astype(np.float32)

        # compute center of mass (intensity-weighted) and shift to center
        total = arr.sum()
        if total > 0:
            ys, xs = np.indices(arr.shape)
            cx = (xs * arr).sum() / total
            cy = (ys * arr).sum() / total
            shiftx = int(round(14.0 - cx))
            shifty = int(round(14.0 - cy))
            arr = np.roll(arr, shift=shifty, axis=0)
            arr = np.roll(arr, shift=shiftx, axis=1)
            if shifty > 0:
                arr[:shifty, :] = 0
            elif shifty < 0:
                arr[shifty:, :] = 0
            if shiftx > 0:
                arr[:, :shiftx] = 0
            elif shiftx < 0:
                arr[:, shiftx:] = 0

        # slight blur to mimic MNIST anti-aliasing
        pil_arr = Image.fromarray(arr.astype(np.uint8))
        pil_arr = pil_arr.filter(ImageFilter.GaussianBlur(radius=0.8))
        arr = np.array(pil_arr).astype(np.float32)

        # normalize
        arr = arr / 255.0

    if show:
        plt.imshow(arr, cmap='gray')
        plt.axis('off')
        if save_preprocessed:
            plt.savefig(save_preprocessed, bbox_inches='tight', pad_inches=0)
        plt.close()

    return arr.reshape(-1, 1)

# pre-processes a folder - cleans up the evaluate_labeled_folder method
def preprocess_folder(folder_path, invert_if_needed=False, exts=('.png','.jpg','.jpeg','.bmp')):
    X_list = []
    filenames = []
    for fname in sorted(os.listdir(folder_path)):
        if not fname.lower().endswith(exts):
            continue
        full = os.path.join(folder_path, fname)
        X_list.append(preprocess_image(full, invert_if_needed=invert_if_needed))
        filenames.append(fname)
    if len(X_list) == 0:
        return None, None
    X = np.concatenate(X_list, axis=1)  # (784, m)
    return X, filenames

# evaluates the neural network for one image
def predict_single_file(img_path, params, invert_if_needed=False):
    X = preprocess_image(img_path, invert_if_needed=invert_if_needed, show=True)
    pred = forward_predict(X, params)  # returns array shape (1,)
    print(f"{os.path.basename(img_path)} -> predicted: {int(pred[0])}")
    return int(pred[0])

# evaluates the neural network for a folder of images
def evaluate_labeled_folder(folder_path, params, invert_if_needed=False):
    X, fnames = preprocess_folder(folder_path, invert_if_needed=invert_if_needed)
    if X is None:
        print("No images found in folder.")
        return
    # predictions
    preds = forward_predict(X, params)
    labels = []
    for f in fnames:
        try:
            # only treat the first character as a label if it is a lone digit (not the start of a number like a year)
            if len(f) > 1 and f[1].isdigit():
                raise ValueError
            labels.append(int(f[0]))
        except:
            labels.append(None)
    labels = np.array(labels, dtype=object)
    mask = np.array([lbl is not None for lbl in labels])
    if mask.sum() > 0:
        acc = np.mean(preds[mask].astype(int) == labels[mask].astype(int)) * 100.0
        print(f"Accuracy on labeled folder '{folder_path}': {acc:.2f}% ({mask.sum()} labeled images)")
    else:
        print("No labeled filenames found (leading digit expected).")
    for fname, p, lbl in zip(fnames, preds, labels):
        print(f"{fname} -> pred={int(p)}  label={lbl}")
    return preds, labels

def main():
    # allows for the user to select files, folders, and directories. If you have a white background, add invert
    parser = argparse.ArgumentParser(description="Test neuralNet forward_predict on images")
    parser.add_argument("--params", default="trained_params.pkl")
    parser.add_argument("--file")
    parser.add_argument("--folder")
    parser.add_argument("--invert", action="store_true")
    args = parser.parse_args()

    # if parameters file is missing -- the network is not trained
    if not os.path.exists(args.params):
        print(f"Parameters file not found: {args.params}")
        return
    params = load_params(args.params)

    # processes user input
    if args.file:
        predict_single_file(args.file, params, invert_if_needed=args.invert)

    if args.folder:
        evaluate_labeled_folder(args.folder, params, invert_if_needed=args.invert)

    if not args.file and not args.folder:
        print("Specify --file IMAGE or --folder PATH. See --help for options.")

if __name__ == "__main__":
    main()
