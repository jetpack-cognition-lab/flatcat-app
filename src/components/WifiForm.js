import InteractButton from './InteractButton'

    // <div>
    // <label>Network:
    // <input
    //   type="text"
    //   value={networkName}
    //   onChange={(e) => setNetworkName(e.target.value)}
    // />
    // </label>
    // <label>Password:
    // <input
    //   type="password"
    //   value={networkSecret}
    //   onChange={(e) => setNetworkSecret(e.target.value)}
    // />
    // </label>
    // <InteractButton
    //   onClick={handleWifiForm}
    //   color={buttonsInteractive[1].color}
    //   label={buttonsInteractive[1].label}
    //   message={buttonsInteractive[1].message}
    //   show_message={buttonsInteractive[1].show_message}
    // />
    // </div>

const WifiForm = ({ networkName, setNetworkName, networkSecret, setNetworkSecret, handleWifiForm, fcuiName, buttonsInteractive }) => {
  return (
    <div>
    <label>Network:
    <input
      type="text"
      name="ssid"
      value={networkName}
      onChange={setNetworkName}
    />
    </label>
    <label>Password:
    <input
      type="password"
      name="psk"
      value={networkSecret}
      onChange={setNetworkSecret}
    />
    </label>
    <InteractButton
      onClick={handleWifiForm}
      color={buttonsInteractive[1].color}
      label={buttonsInteractive[1].label}
      message={buttonsInteractive[1].message}
      show_message={buttonsInteractive[1].show_message}
    />
    </div>
  )
}

export default WifiForm
