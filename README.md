[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

# Headscale Monitor for Home Assistant

This integration connects to the API of your Headscale server to monitor the devices in your Headscale network. It is based on the [official Tailscale integration](https://www.home-assistant.io/integrations/tailscale/).

**Note**: This integration does not provide access to your Headscale network! If you want to access the network from Home Assistant, you have to install the Tailscale client.

## Configuration

This integration can be configured directly in Home Assistant via HACS:

1. Go to `HACS` -> `Integrations` -> Click on the three dots in the top right corner --> Click on `Userdefined repositories`
1. Insert `https://github.com/Tidone/homeassistant_headscale` into the field `Repository`
1. Choose `Integration` in the dropdown field `Category`.
1. Click on the `Add` button.
1. Then search for the new added `Headscale` integration, click on it and the click on the button `Download` on the bottom right corner
1. Restart Home Assistant when it says to.
1. In Home Assistant, go to `Configuration` -> `Integrations` -> Click `+ Add Integration`
   Search for `Headscale Monitor` and follow the instructions.
   - You have to provide the Headscale Server URL and your access token in the respective fields
   - Please refer to the [Headscale Docs](https://headscale.net/stable/ref/api/) for how to create an access token.
   - The default expiration is 90 days, which means that after 90 days you have to create a new access token, delete the integration and add it again with the new token.
   - You can also generate tokens with longer expiration dates by adding the `--expiration` argument to the `apikeys create` command (e.g. `headscale apikeys create --expiration 999d`)

## Provided sensors

This integration creates the following sensors for each Headscale node:

- Connection status: Whether the node is online or offline
- Last seen: Timestamp when the node was last active
- Ip address: Internal Headscale IP address
- Expiration date: Timestamp when the node will expire
