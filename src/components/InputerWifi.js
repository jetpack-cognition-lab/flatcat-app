// import React, { useState } from "react"
import React from "react"

const InputerWifi = ({ ssid, psk, scan_ssid, id_str }) => {
    // const [input, setInput] = useState(Value)

  return (
    <form>
      <div>
        <input
        type='text'
        value={ssid}
        onChange={(e) => console.log(e.target.value)} />
        <input
        type='text'
        value={psk}
        onChange={(e) => console.log(e.target.value)} />
        <input
        type='text'
        value={scan_ssid}
        onChange={(e) => console.log(e.target.value)} />
        <input
        type='text'
        value={id_str}
        onChange={(e) => console.log(e.target.value)} />
      </div>
    </form>
  )
}

export default InputerWifi
