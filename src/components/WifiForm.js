import InteractButton from './InteractButton'


const WifiForm = ({ networkName, setNetworkName, networkSecret, setNetworkSecret, handleWifiForm, fcuiName }) => {

  return (
    <form onSubmit={handleWifiForm}>
    <label>Network:
    <input
      type="text"
      value={networkName}
      onChange={(e) => setNetworkName(e.target.value)}
    />
    </label>
    <label>Password:
    <input
      type="password"
      value={networkSecret}
      onChange={(e) => setNetworkSecret(e.target.value)}
    />
    </label>
    <InteractButton type='submit' color='green' show_message={false} label='connect' message={fcuiName+' is connected to the internet'} />
    </form>
  )
}

export default WifiForm
