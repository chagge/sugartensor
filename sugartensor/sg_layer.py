# -*- coding: utf-8 -*-
import sugartensor as tf
import sg_initializer as init


__author__ = 'buriburisuri@gmail.com'


#
# neural network layers
#


@tf.sg_layer_func
def sg_bypass(tensor, opt):
    r"""Returns the input tensor itself.
    
    Args:
      tensor: A `Tensor`.
    
    Returns:
      The same tensor as `tensor`.
    """
    return tensor


@tf.sg_layer_func
def sg_dense(tensor, opt):
    r"""Applies a full connection.
    
    Args:
      tensor: A 2-D `Tensor`.
      in_dim: An `integer`. The size of input dimension.
      dim: An `integer`. The size of output dimension.
      bias: Boolean. If True, biases are added. 
      
    Returns:
      A `Tensor` with the same type as `tensor`.
    """
    # parameter initialize
    w = init.he_uniform('W', (opt.in_dim, opt.dim))
    if opt.bias:
        b = init.constant('b', opt.dim)

    # apply transform
    out = tf.matmul(tensor, w) + (b if opt.bias else 0)

    return out


@tf.sg_layer_func
def sg_conv(tensor, opt):
    r"""Applies a 2-D convolution.
    
    Args:
      tensor: A 4-D `Tensor`.
      size: A tuple or list of integers of length 2 representing `[kernel height, kernel width]`.
        Can be an int if both values are the same.
        If not specified, (3, 3) is set implicitly.
      stride: A tuple or list of integers of length 2 or 4 representing stride dimensions.
        If the length is 2, i.e., (a, b), the stride is `[1, a, b, 1]`.
        If the length is 4, i.e., (a, b, c, d), the stride is `[a, b, c, d]`.
        Can be an int. If the length is an int, i.e., a, the stride is `[1, a, a, 1]`.
        The default value is [1, 1, 1, 1].
      in_dim: An `integer`. The size of input dimension.
      dim: An `integer`. The size of output dimension.
      pad: Either `SAME` (Default) or `VALID`. 
      bias: Boolean. If True, biases are added.

    Returns:
      A `Tensor` with the same type as `tensor`.
    """
    # default options
    opt += tf.sg_opt(size=(3, 3), stride=(1, 1, 1, 1), pad='SAME')
    opt.size = opt.size if isinstance(opt.size, (tuple, list)) else [opt.size, opt.size]
    opt.stride = opt.stride if isinstance(opt.stride, (tuple, list)) else [1, opt.stride, opt.stride, 1]
    opt.stride = [1, opt.stride[0], opt.stride[1], 1] if len(opt.stride) == 2 else opt.stride

    # parameter initialize
    w = init.he_uniform('W', (opt.size[0], opt.size[1], opt.in_dim, opt.dim))
    if opt.bias:
        b = init.constant('b', opt.dim)

    # apply convolution
    out = tf.nn.conv2d(tensor, w, strides=opt.stride, padding=opt.pad) + (b if opt.bias else 0)

    return out


@tf.sg_layer_func
def sg_conv1d(tensor, opt):
    r"""Applies a 1-D convolution.
    
    Args:
      tensor: A `Tensor`.
      size: An `integer` representing `[kernel width]`.
        If not specified, 2 is set implicitly.
      stride: An `integer`. The number of entries by which
        the filter is moved right at each step.
      in_dim: An `integer`. The size of input dimension.
      dim: An `integer`. The size of output dimension.
      pad: Either `SAME` (Default) or `VALID`.
      bias: Boolean. Whether to add biases to the filters.
      
    Returns:
      A `Tensor` with the same type as `tensor`.
    """
    # default options
    opt += tf.sg_opt(size=2, stride=1, pad='SAME')

    # parameter initialize
    w = init.he_uniform('W', (opt.size, opt.in_dim, opt.dim))
    if opt.bias:
        b = init.constant('b', opt.dim)

    # apply convolution
    out = tf.nn.conv1d(tensor, w, stride=opt.stride, padding=opt.pad) + (b if opt.bias else 0)

    return out


@tf.sg_layer_func
def sg_aconv(tensor, opt):
    r"""Applies a 2-D atrous (or dilated) convolution.
    
    Args:
      tensor: A 4-D `Tensor`.
      size: A tuple or list of integers of length 2 representing `[kernel height, kernel width]`.
        Can be an int if both values are the same.
        If not specified, (3, 3) is set automatically.
      rate: A positive int32. The stride with which we sample input values across
        the `height` and `width` dimensions. Default is 2.
      in_dim: An `integer`. The size of input dimension.
      dim: An `integer`. The size of output dimension.
      pad: Either `SAME` (Default) or `VALID`.
      bias: Boolean. Whether to add biases to the filters.
            
    Returns:
      A `Tensor` with the same type as `tensor`.
    """
    # default options
    opt += tf.sg_opt(size=(3, 3), rate=2, pad='SAME')
    opt.size = opt.size if isinstance(opt.size, (tuple, list)) else [opt.size, opt.size]

    # parameter initialize
    w = init.he_uniform('W', (opt.size[0], opt.size[1], opt.in_dim, opt.dim))
    if opt.bias:
        b = init.constant('b', opt.dim)

    # apply convolution
    out = tf.nn.atrous_conv2d(tensor, w, rate=opt.rate, padding=opt.pad) + (b if opt.bias else 0)

    return out


@tf.sg_layer_func
def sg_aconv1d(tensor, opt):
    r"""Applies 1-D atrous (or dilated) convolution.
    
    Args:
      tensor: A 3-D `Tensor`.
      causal: Boolean. If True, zeros are padded before the time axis such that
        each activation unit doesn't have receptive neurons beyond the equivalent time step.
      size: An `integer` representing `[kernel width]`. As a default it is set to 2
        if causal is True, 3 otherwise. 
      rate: A positive int32. The stride with which we sample input values across
        the `height` and `width` dimensions. Default is 1.
      in_dim: An `integer`. The size of input dimension.
      dim: An `integer`. The size of output dimension.
      pad: Either `SAME` (Default) or `VALID`.
      bias: Boolean. Whether to add biases to the filters.
            
    Returns:
      A `Tensor` with the same type as `tensor`.
    """
    # default options
    opt += tf.sg_opt(size=(2 if opt.causal else 3), rate=1, pad='SAME')

    # parameter initialize
    w = init.he_uniform('W', (1, opt.size, opt.in_dim, opt.dim))
    if opt.bias:
        b = init.constant('b', opt.dim)

    if opt.causal:
        # pre-padding for causality
        if opt.pad == 'SAME':
            pad_len = (opt.size - 1) * opt.rate  # padding size
            x = tf.pad(tensor, [[0, 0], [pad_len, 0], [0, 0]]).sg_expand_dims(dim=1)
        else:
            x = tensor.sg_expand_dims(dim=1)
        # apply 2d convolution
        out = tf.nn.atrous_conv2d(x, w, rate=opt.rate, padding='VALID') + (b if opt.bias else 0)
    else:
        # apply 2d convolution
        out = tf.nn.atrous_conv2d(tensor.sg_expand_dims(dim=1),
                                  w, rate=opt.rate, padding=opt.pad) + (b if opt.bias else 0)
    # reduce dimension
    out = out.sg_squeeze(dim=1)

    return out


@tf.sg_layer_func
def sg_upconv(tensor, opt):
    r"""Applies a upconvolution (or convolution transpose).
    
    Args:
      tensor: A 4-D `Tensor`.
      size: A tuple or list of integers of length 2 representing `[kernel height, kernel width]`.
        Can be an int if both values are the same.
        If not specified, (3, 3) is set implicitly.
        The default value is [1, 2, 2, 1].
      stride: A tuple or list of integers of length 2 or 4 representing stride dimensions.
        If the length is 2, i.e., (a, b), the stride is `[1, a, b, 1]`.
        If the length is 4, i.e., (a, b, c, d), the stride is `[a, b, c, d]`.
        Can be an int. If the length is an int, i.e., a, the stride is `[1, a, a, 1]`.
      in_dim: A positive `integer`. The size of input dimension.
      dim: A positive `integer`. The size of output dimension.
      pad: Either `SAME` (Default) or `VALID`. 
      bias: Boolean. If True, biases are added.
            
    Returns:
      A `Tensor` with the same type as `tensor`.
    """
    # default options
    opt += tf.sg_opt(size=(3, 3), stride=(1, 2, 2, 1), pad='SAME')
    opt.size = opt.size if isinstance(opt.size, (tuple, list)) else [opt.size, opt.size]
    opt.stride = opt.stride if isinstance(opt.stride, (tuple, list)) else [1, opt.stride, opt.stride, 1]
    opt.stride = [1, opt.stride[0], opt.stride[1], 1] if len(opt.stride) == 2 else opt.stride

    # parameter initialize
    w = init.he_uniform('W', (opt.size[0], opt.size[1], opt.dim, opt.in_dim))
    if opt.bias:
        b = init.constant('b', opt.dim)

    # tedious shape handling for conv2d_transpose
    shape = tensor.get_shape().as_list()
    out_shape = [tf.shape(tensor)[0], shape[1] * opt.stride[1], shape[2] * opt.stride[2], opt.dim]

    # apply convolution
    out = tf.nn.conv2d_transpose(tensor, w, output_shape=tf.pack(out_shape),
                                 strides=opt.stride, padding=opt.pad) + (b if opt.bias else 0)
    # reset shape is needed because conv2d_transpose() erase all shape information.
    out.set_shape([None, out_shape[1], out_shape[2], opt.dim])

    return out


#
# RNN layers
#

def sg_emb(**kwargs):
    r"""Returns an embedding layer or a look-up table.
    
    Args:
      name: A name for the layer (required).
      emb: A 2-D array. Has the shape of `[vocabulary size -1, embedding dimension size]`.
        Note that the first row is filled with 0's because they correspond to padding.
      in_dim: A positive `integer`. The size of input dimension.
      dim: A positive `integer`. The size of output dimension.
      voca_size: A positive int32.
      
    Returns:
      A 2-D tensor.
    """
    opt = tf.sg_opt(kwargs)
    assert opt.name is not None, 'name is mandatory.'

    import sg_initializer as init

    if opt.emb is None:
        # initialize embedding matrix
        assert opt.voca_size is not None, 'voca_size is mandatory.'
        assert opt.dim is not None, 'dim is mandatory.'
        w = init.he_uniform(opt.name, (opt.voca_size-1, opt.dim))
    else:
        # use given embedding matrix
        w = init.external(opt.name, value=opt.emb)

    # 1st row should be zero and not be updated by backprop because of zero padding.
    emb = tf.concat(0, [tf.zeros((1, opt.dim), dtype=tf.sg_floatx), w])

    return emb


# layer normalization for rnn
def _ln_rnn(x, gamma, beta):
    r"""Applies layer normalization.
    Normalizes the last dimension of the tensor `x`.
    
    Args:
      x: A `Tensor`.
      gamma: A `Tensor` constant. Scale parameter.
      beta: A `Tensor` constant. Offset parameter.
    
    Returns:
      A `Tensor` with the same shape as `x`.
    """
    # calc layer mean, variance for final axis
    mean, variance = tf.nn.moments(x, axes=[len(x.get_shape()) - 1], keep_dims=True)

    # apply layer normalization
    x = (x - mean) / tf.sqrt(variance + tf.sg_eps)

    # apply parameter
    return gamma * x + beta


@tf.sg_rnn_layer_func
def sg_rnn(tensor, opt):
    r"""Applies a simple rnn.
    
    Args:
      tensor: A 3-D `Tensor`.
      in_dim: A positive `integer`. The size of input dimension.
      dim: A positive `integer`. The size of output dimension.
      bias: Boolean. If True, biases are added.
      ln: Boolean. If True, layer normalization is applied.   
      init_state: A 2-D `Tensor`. If None, the initial state is set to zeros.
      last_only: Boolean. If True, the outputs in the last time step are returned.
    
    Returns:
      A `Tensor`. If last_only is False, the output tensor has shape [batch size, time steps, dim].
        If last_only is True, the shape will be [batch size, dim].
    """
    # layer normalization
    ln = lambda v: _ln_rnn(v, gamma, beta) if opt.ln else v
    # step function
    def step(h, x):
        # simple rnn
        ### Replace tensor[:, i, :] with x. bryan ###
        y = ln(tf.matmul(tensor[:, i, :], w) + tf.matmul(h, u) + (b if opt.bias else 0))
        return y

    # parameter initialize
    w = init.orthogonal('W', (opt.in_dim, opt.dim))
    u = init.identity('U', opt.dim)
    if opt.bias:
        b = init.constant('b', opt.dim)

    # layer normalization parameters
    if opt.ln:
        # offset, scale parameter
        beta = init.constant('beta', opt.dim)
        gamma = init.constant('gamma', opt.dim, value=1)

    # initial state
    init_h = opt.init_state if opt.init_state is not None \
        else tf.zeros((tensor.get_shape().as_list()[0], opt.dim), dtype=tf.sg_floatx)

    # do rnn loop
    h, out = init_h, []
    for i in range(tensor.get_shape().as_list()[1]):
        # apply step func
        h = step(h, tensor[:, i, :])
        # save result
        out.append(h.sg_expand_dims(dim=1))

    # merge tensor
    if opt.last_only:
        out = out[-1].sg_squeeze(dim=1)
    else:
        out = tf.concat(1, out)

    return out


@tf.sg_rnn_layer_func
def sg_gru(tensor, opt):
    r"""Applies a GRU.
    
    Args:
      tensor: A 3-D `Tensor`.
      in_dim: A positive `integer`. The size of input dimension.
      dim: A positive `integer`. The size of output dimension.
      bias: Boolean. If True, biases are added.
      ln: Boolean. If True, layer normalization is applied.   
      init_state: A 2-D `Tensor`. If None, the initial state is set to zeros.
      last_only: Boolean. If True, the outputs in the last time step are returned.
    
    Returns:
      A `Tensor`. If last_only is False, the output tensor has shape [batch size, time steps, dim].
        If last_only is True, the shape will be [batch size, dim].
    """
    
    # layer normalization
    ln = lambda v: _ln_rnn(v, gamma, beta) if opt.ln else v

    # step func
    def step(h, x):
        # update gate
        z = tf.sigmoid(ln(tf.matmul(x, w_z) + tf.matmul(h, u_z) + (b_z if opt.bias else 0)))
        # reset gate
        r = tf.sigmoid(ln(tf.matmul(x, w_r) + tf.matmul(h, u_r) + (b_r if opt.bias else 0)))
        # h_hat
        hh = tf.tanh(ln(tf.matmul(x, w_h) + tf.matmul(r*h, u_h) + (b_h if opt.bias else 0)))
        # final output
        y = (1. - z) * h + z * hh
        return y

    # parameter initialize
    w_z = init.orthogonal('W_z', (opt.in_dim, opt.dim))
    u_z = init.identity('U_z', opt.dim)
    w_r = init.orthogonal('W_r', (opt.in_dim, opt.dim))
    u_r = init.identity('U_r', opt.dim)
    w_h = init.orthogonal('W_h', (opt.in_dim, opt.dim))
    u_h = init.identity('U_h', opt.dim)
    if opt.bias:
        b_z = init.constant('b_z', opt.dim)
        b_r = init.constant('b_r', opt.dim)
        b_h = init.constant('b_h', opt.dim)

    # layer normalization parameters
    if opt.ln:
        # offset, scale parameter
        beta = init.constant('beta', opt.dim)
        gamma = init.constant('gamma', opt.dim, value=1)

    # initial state
    init_h = opt.init_state if opt.init_state is not None \
        else tf.zeros((tensor.get_shape().as_list()[0], opt.dim), dtype=tf.sg_floatx)

    # do rnn loop
    h, out = init_h, []
    for i in range(tensor.get_shape().as_list()[1]):
        # apply step function
        h = step(h, tensor[:, i, :])
        # save result
        out.append(h.sg_expand_dims(dim=1))

    # merge tensor
    if opt.last_only:
        out = out[-1].sg_squeeze(dim=1)
    else:
        out = tf.concat(1, out)

    return out


@tf.sg_rnn_layer_func
def sg_lstm(tensor, opt):
    r"""Applies an LSTM.

    Args:
      tensor: A 3-D `Tensor`.
      in_dim: A positive `integer`. The size of input dimension.
      dim: A positive `integer`. The size of output dimension.
      bias: Boolean. If True, biases are added.
      ln: Boolean. If True, layer normalization is applied.   
      init_state: A 2-D `Tensor`. If None, the initial state is set to zeros.
      last_only: Boolean. If True, the outputs in the last time step are returned.
    
    Returns:
      A `Tensor`. If last_only is False, the output tensor has shape [batch size, time steps, dim].
        If last_only is True, the shape will be [batch size, dim].
    """
    # layer normalization
    ln = lambda v: _ln_rnn(v, gamma, beta) if opt.ln else v

    # step func
    def step(h, c, x):
        # forget gate
        f = tf.sigmoid(ln(tf.matmul(x, w_f) + tf.matmul(h, u_f) + (b_f if opt.bias else 0)))
        # input gate
        i = tf.sigmoid(ln(tf.matmul(x, w_i) + tf.matmul(h, u_i) + (b_i if opt.bias else 0)))
        # new cell value
        cc = tf.tanh(ln(tf.matmul(x, w_c) + tf.matmul(h, u_c) + (b_c if opt.bias else 0)))
        # out gate
        o = tf.sigmoid(ln(tf.matmul(x, w_o) + tf.matmul(h, u_o) + (b_o if opt.bias else 0)))
        # cell update
        cell = f * c + i * cc
        # final output
        y = o * tf.tanh(cell)
        return y, cell

    # parameter initialize
    w_i = init.orthogonal('W_i', (opt.in_dim, opt.dim))
    u_i = init.identity('U_i', opt.dim)
    w_f = init.orthogonal('W_f', (opt.in_dim, opt.dim))
    u_f = init.identity('U_f', opt.dim)
    w_o = init.orthogonal('W_o', (opt.in_dim, opt.dim))
    u_o = init.identity('U_o', opt.dim)
    w_c = init.orthogonal('W_c', (opt.in_dim, opt.dim))
    u_c = init.identity('U_c', opt.dim)
    if opt.bias:
        b_i = init.constant('b_i', opt.dim)
        b_f = init.constant('b_f', opt.dim)
        b_o = init.constant('b_o', opt.dim, value=1)
        b_c = init.constant('b_c', opt.dim)

    # layer normalization parameters
    if opt.ln:
        # offset, scale parameter
        beta = init.constant('beta', opt.dim)
        gamma = init.constant('gamma', opt.dim, value=1)

    # initial state
    init_h = opt.init_state if opt.init_state is not None \
        else tf.zeros((tensor.get_shape().as_list()[0], opt.dim), dtype=tf.sg_floatx)

    # do rnn loop
    h, c, out = init_h, init_h, []
    for i in range(tensor.get_shape().as_list()[1]):
        # apply step function
        h, c = step(h, c, tensor[:, i, :])
        # save result
        out.append(h.sg_expand_dims(dim=1))

    # merge tensor
    if opt.last_only:
        out = out[-1].sg_squeeze(dim=1)
    else:
        out = tf.concat(1, out)

    return out

