# 06 When a device won't talk

The order I work through. Each step rules out one layer, so I try not to skip ahead.

1. **Cable and link lights.** Boring, and still the cause more often than expected.
2. **Same network?** `ipconfig` on the laptop. A laptop on `192.168.0.250/24` cannot reach `192.168.1.10` without a route. A `169.254.x.x` address means the adapter got no DHCP and has no real address.
3. **Ping.** `ping 192.168.0.10`. Some devices ignore ping, so a failure is only a hint.
4. **Find the device.** If you don't know its IP, ping the whole subnet so the ARP table fills, then read it:
   ```
   for /L %i in (1,1,254) do @ping -n 1 -w 100 192.168.0.%i | find "TTL"
   arp -a
   ```
   (In a batch file, write `%%i`.) The MAC address prefix tells you the manufacturer. The ARP table is a cache of recent contacts, so run the sweep first.
5. **Is the port open?** PowerShell: `Test-NetConnection 192.168.0.10 -Port 502`. Common ports: Modbus TCP 502, S7 102, OPC UA 4840.
6. **Is the protocol switched on in the device, and over which transport?** Many PLCs ship with it off. SLMP and some others can be TCP or UDP.
7. **Identifiers.** Unit ID, station number, rack and slot, NodeId. A wrong one gives silence or an exception.
8. **Address and function.** Address base, FC 3 versus FC 4, device code.
9. **Decode.** Signed or unsigned, word order, scaling factor.
10. **Timing.** Timeouts, polling interval, retries. Many devices accept only a few simultaneous connections, so make sure another master is not holding them.

Before step 9, find one value you can see on the device's display and make your reading match it. That settles address, type and word order at once, and it gives you something to compare against later.

Write down the settings that finally worked. The next machine of the same type usually behaves the same.
