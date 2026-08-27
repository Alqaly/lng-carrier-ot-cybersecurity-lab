@load base/protocols/modbus
@load policy/protocols/modbus/known-masters-slaves
@load policy/protocols/modbus/track-memmap

# The lab intentionally uses separate non-default ports per process domain.
redef Modbus::ports += { 5020/tcp, 5021/tcp, 5022/tcp };
