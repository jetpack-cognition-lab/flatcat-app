const TachoScale = ({ dataValue, limitLow, limitHigh, scaleClockFace }) => {
  let turnNeadle = -20
  let needleClass = 'tacho_needle'
  if (dataValue >= limitLow && dataValue <= limitHigh) {
    turnNeadle = dataValue / 2.5 - 20
  } else if (dataValue < limitLow) {

    // TODO: timing of css transitions for needle

    turnNeadle = -21
    needleClass += ' too_little'
  } else if ( dataValue > limitHigh) {
    turnNeadle = 21
    needleClass += ' too_much'
  }
  return (
    <div className="tacho_wrap">
    <div className="the_clipper">
    <div className="tacho_border_circ top"></div>
    <div className="tacho_border_line left"></div>
    <div className="tacho_border_line right"></div>
    <div className="tacho_border_circ bottom"></div>
    <div
      className={needleClass}
      style={{transform: `rotate(${turnNeadle}deg)`}}
    ></div>
    <div className="clockFace">{scaleClockFace}</div>
    <div className="tacho_scale_wrap">
    <div className="tacho_scale_dot"></div>
    <div className="tacho_scale_dot small"></div>
    <div className="tacho_scale_dot small"></div>
    <div className="tacho_scale_dot small"></div>
    <div className="tacho_scale_dot small"></div>
    <div className="tacho_scale_dot"></div>
    <div className="tacho_scale_dot small"></div>
    <div className="tacho_scale_dot small"></div>
    <div className="tacho_scale_dot small"></div>
    <div className="tacho_scale_dot small"></div>
    <div className="tacho_scale_dot"></div>
    </div>
    </div>
    </div>
  )
}

export default TachoScale
