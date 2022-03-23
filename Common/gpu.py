import os
import torch


def check_for_GPU():
    # Get the GPU device name.
    try:
        import tensorflow as tf
        device_name = tf.test.gpu_device_name()
    except:
        device_name = "/device:CPU:0"

    if device_name == '/device:GPU:0':
        print('Found GPU at: {}'.format(device_name))
    else:
        print("No GPU found, using CPU")

    # If there's a GPU available...
    # Don't actually use the TF device since we don't know which backend torch
    # may use
    if torch.cuda.is_available():
        # Tell PyTorch to use the GPU.
        device = torch.device("cuda")
        print('There are %d GPU(s) available.' % torch.cuda.device_count())
        print('We will use the GPU:', torch.cuda.get_device_name(0))
    else:
        print('No GPU available, using the CPU instead.')
        device = torch.device("cpu")

    # Determine run environment
    if 'COLAB_TPU_ADDR' in os.environ and os.environ['COLAB_TPU_ADDR']:
        strategy = _get_tpu_strategy()
        print('Using TPU')
    elif _tf_gpu_avail():
        strategy = _get_gpu_strategy()
        print('Using GPU')
    else:
        print('Using CPU.  NOT RECOMMENDED')
        strategy = _get_cpu_strategy()

    return device, strategy


def _tf_gpu_avail():
    try:
        import tensorflow as tf
        return tf.test.is_gpu_available()
    except:
        return False


def _get_tpu_strategy():
    try:
        import tensorflow as tf
        cluster_resolver = tf.distribute.cluster_resolver.TPUClusterResolver(tpu='')
        tf.config.experimental_connect_to_cluster(cluster_resolver)
        tf.tpu.experimental.initialize_tpu_system(cluster_resolver)
        strategy = tf.distribute.TPUStrategy(cluster_resolver)
        return strategy
    except:
        return None


def _get_gpu_strategy():
    try:
        import tensorflow as tf
        strategy = tf.distribute.MirroredStrategy()
        return strategy
    except:
        return None


def _get_cpu_strategy():
    try:
        import tensorflow as tf
        strategy = tf.distribute.OneDeviceStrategy
        return strategy
    except:
        return None
