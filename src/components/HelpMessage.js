import SVGseparator from './SVGseparator'

const HelpMessage = ({ helpMessage }) => {
  return (
    <section className='help_message_section'>
    <p>{helpMessage}</p>
    <SVGseparator a={20} b={60} c={30} d={82} width={18} />
    </section>
  )
}

export default HelpMessage
