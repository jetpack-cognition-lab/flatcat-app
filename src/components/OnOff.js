const OnOff = ({ onOffOption, onClick }) => {
  return (
    <div className='fc_btn_onoff_wrap'>
      <div className='explaination'>
        <p>{onOffOption.help}</p>
      </div>
      <button
        className="fc_btn_onoff"
        value={onOffOption.value}
        onClick={onClick}
      >
      {onOffOption.value ? 'on' : 'off'}
      </button>
      <p>{onOffOption.name}</p>
    </div>
  )
}

export default OnOff
